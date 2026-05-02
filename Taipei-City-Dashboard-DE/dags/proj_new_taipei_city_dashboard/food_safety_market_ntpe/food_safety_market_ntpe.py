from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import io
    import pandas as pd
    import re
    import requests
    import zipfile
    from xml.etree import ElementTree as ET
    from sqlalchemy import create_engine
    from utils.extract_stage import NewTaipeiAPIClient
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_address import (
        clean_data,
        get_addr_xy_parallel,
        main_process,
        save_data,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    rid = "785be91a-caaf-4e1c-91d6-f7d616d31a45"
    from_crs = 4326
    geometry_type = "Point"
    stall_cols = [
        "stall_total",
        "produce_stalls",
        "meat_stalls",
        "seafood_stalls",
        "poultry_stalls",
        "grain_stalls",
        "grocery_stalls",
        "flower_stalls",
        "food_stalls",
        "general_merchandise_stalls",
        "other_stalls",
        "vacant_stalls",
    ]

    def _extract_hidden_inputs(html):
        inputs = {}
        for match in re.finditer(r"<input[^>]+>", html):
            tag = match.group(0)
            name = re.search(r'name="([^"]+)"', tag)
            if not name:
                continue
            value = re.search(r'value="([^"]*)"', tag)
            inputs[name.group(1)] = value.group(1) if value else ""
        return inputs

    def _download_latest_stall_ods():
        report_url = "https://oas.bas.ntpc.gov.tw/NTPCTRWD/NewPage/kcg08.aspx"
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        response = session.get(report_url, timeout=60)
        response.raise_for_status()
        data = _extract_hidden_inputs(response.text)

        last_year = pd.Timestamp.now(tz="Asia/Taipei").year - 1
        data.update(
            {
                "ctl00$ContentPlaceHolder1$txtRptNo": "21412-02-01-2",
                "ctl00$ContentPlaceHolder1$txtRptName": "",
                "ctl00$ContentPlaceHolder1$ddlOrg": "382170000G",
                "ctl00$ContentPlaceHolder1$ddlYearMonth": (
                    f"{last_year}-01-01~{last_year}-12-31"
                ),
                "ctl00$ContentPlaceHolder1$btnGo": "查詢",
            }
        )
        response = session.post(report_url, data=data, timeout=60)
        response.raise_for_status()
        match = re.search(
            r"21412-02-01-2.*?href=\"([^\"]*DownloadHandler\.aspx[^\"]+)\"",
            response.text,
            re.S,
        )
        if not match:
            raise ValueError("Unable to find New Taipei market stall ODS download link.")

        download_url = requests.compat.urljoin(report_url, match.group(1))
        response = session.get(download_url, timeout=60)
        response.raise_for_status()
        return response.content

    def _parse_stall_ods(ods_content):
        ns = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        }
        districts = [
            "板橋",
            "三重",
            "中和",
            "永和",
            "新莊",
            "新店",
            "土城",
            "蘆洲",
            "樹林",
            "鶯歌",
            "三峽",
            "淡水",
            "汐止",
            "瑞芳",
            "五股",
            "泰山",
            "林口",
            "深坑",
            "石碇",
            "坪林",
            "三芝",
            "石門",
            "八里",
            "平溪",
            "雙溪",
            "貢寮",
            "金山",
            "萬里",
            "烏來",
        ]

        def split_market_name(full_name):
            for district in sorted(districts, key=len, reverse=True):
                if full_name.startswith(f"{district}區"):
                    return f"{district}區", full_name[len(f"{district}區") :]
                if full_name.startswith(district):
                    return f"{district}區", full_name[len(district) :]
            return "", full_name

        root = ET.fromstring(zipfile.ZipFile(io.BytesIO(ods_content)).read("content.xml"))
        rows = []
        for row in root.findall(".//table:table-row", ns):
            cells = []
            for cell in row.findall("table:table-cell", ns):
                repeat = int(
                    cell.attrib.get(
                        "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
                        "number-columns-repeated",
                        "1",
                    )
                )
                text = "".join(cell.itertext()).strip()
                value = (
                    cell.attrib.get(
                        "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value"
                    )
                    or text
                )
                cells.extend([value] * min(repeat, 20))

            if len(cells) < 13 or not str(cells[1]).isdigit():
                continue
            district, name = split_market_name(cells[0])
            rows.append(
                {
                    "district": district,
                    "name": name,
                    "stall_total": cells[1],
                    "produce_stalls": cells[2],
                    "meat_stalls": cells[3],
                    "seafood_stalls": cells[4],
                    "poultry_stalls": cells[5],
                    "grain_stalls": cells[6],
                    "grocery_stalls": cells[7],
                    "flower_stalls": cells[8],
                    "food_stalls": cells[9],
                    "general_merchandise_stalls": cells[10],
                    "other_stalls": cells[11],
                    "vacant_stalls": cells[12],
                }
            )
        return pd.DataFrame(rows)

    def _normalize_market_name(name):
        normalized = str(name).strip()
        for token in ["公有零售市場", "公有市場", "零售市場", "公有", "零售", "市場", "2樓"]:
            normalized = normalized.replace(token, "")
        return normalized.strip()

    client = NewTaipeiAPIClient(rid, input_format="json")
    raw_data = pd.DataFrame(client.get_all_data(size=1000))

    data = raw_data.rename(
        columns={
            "item": "market_id",
            "name": "name",
            "county": "city",
            "countycode": "city_code",
            "town": "district",
            "areacode": "district_code",
            "address": "address",
            "phone": "phone",
            "types": "type",
        }
    )

    for col in ["market_id", "name", "city", "district", "address", "phone", "type"]:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["data_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    lasttime_in_data = data["data_time"].max()
    data["city"] = data["city"].replace({"新北市": "新北市"})
    data["address"] = data["address"].where(
        data["address"].str.startswith("新北市"),
        "新北市" + data["district"] + data["address"],
    )

    stall_data = _parse_stall_ods(_download_latest_stall_ods())
    stall_data["market_key"] = stall_data["name"].apply(_normalize_market_name)
    data["market_key"] = data["name"].apply(_normalize_market_name)
    data.loc[
        (data["district"] == "金山區") & (data["market_key"] == "第一"),
        "market_key",
    ] = "金山"
    stall_data = stall_data.drop_duplicates(subset=["district", "market_key"])
    data = data.merge(
        stall_data.drop(columns=["name"]),
        on=["district", "market_key"],
        how="left",
    )
    for col in stall_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    addr = data["address"]
    addr_cleaned = clean_data(addr)
    standard_addr_list = main_process(addr_cleaned)
    _, output = save_data(addr, addr_cleaned, standard_addr_list)
    data["address"] = output

    unique_addresses = pd.Series(data["address"].dropna().unique())
    lng, lat = get_addr_xy_parallel(unique_addresses, sleep_time=0.5)
    geocoded = pd.DataFrame({"address": unique_addresses, "lng": lng, "lat": lat})
    data = data.merge(geocoded, on="address", how="left")
    data = data.dropna(subset=["lng", "lat"])
    if data.empty:
        raise ValueError("No New Taipei market records were geocoded successfully.")

    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=from_crs,
    )
    ready_data = gdata[
        [
            "data_time",
            "market_id",
            "name",
            "city",
            "city_code",
            "district",
            "district_code",
            "address",
            "phone",
            "type",
            "stall_total",
            "produce_stalls",
            "meat_stalls",
            "seafood_stalls",
            "poultry_stalls",
            "grain_stalls",
            "grocery_stalls",
            "flower_stalls",
            "food_stalls",
            "general_merchandise_stalls",
            "other_stalls",
            "vacant_stalls",
            "lng",
            "lat",
            "wkb_geometry",
        ]
    ]

    engine = create_engine(ready_data_db_uri)
    save_geodataframe_to_postgresql(
        engine,
        gdata=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
        geometry_type=geometry_type,
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, lasttime_in_data)


dag = CommonDag(
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="food_safety_market_ntpe",
)
dag.create_dag(etl_func=_transfer)
