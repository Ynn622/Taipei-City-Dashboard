from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import io
    import html as html_lib
    import pandas as pd
    import re
    import requests
    import zipfile
    from xml.etree import ElementTree as ET
    from sqlalchemy import create_engine
    from utils.district_geocoder import DISTRICT_CENTROIDS
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

    def _get_html_attr(tag, attr):
        """取出 HTML tag 的指定 attribute，並處理 HTML escape。"""
        match = re.search(
            rf"{attr}\s*=\s*(['\"])(.*?)\1",
            tag,
            re.I | re.S,
        )
        return html_lib.unescape(match.group(2)) if match else ""

    def _find_stall_download_link(page_html):
        """從統計發布頁表格中找到目標 ODS 下載連結。"""
        report_name = "新北市各區公有零售市場攤位數"
        expected_filename = f"{report_name}.ods"
        rows = re.findall(r"<tr\b.*?</tr>", page_html, re.I | re.S)
        for row in rows:
            if report_name not in row:
                continue
            for tag in re.findall(r"<a\b[^>]*>", row, re.I | re.S):
                href = _get_html_attr(tag, "href")
                title = _get_html_attr(tag, "title")
                if expected_filename == title and "DownloadHandler.aspx" in href:
                    return href
        return ""

    def _download_latest_stall_ods():
        """下載去年發布的市場攤位數 ODS。"""
        report_year = pd.Timestamp.now(tz="Asia/Taipei").year - 1
        report_url = (
            "https://oas.bas.ntpc.gov.tw/NTPCTRWD/NewPage/Publish.aspx"
            f"?Mid1=382170000G&p=0&y={report_year}%2f12%2f25&s=50"
        )
        print(f"[food_safety_market_ntpe] Fetch stall report page: {report_url}")
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        response = session.get(report_url, timeout=60)
        response.raise_for_status()
        download_link = _find_stall_download_link(response.text)
        if not download_link:
            raise ValueError(
                "Unable to find New Taipei market stall ODS download link "
                f"for report year {report_year}."
            )

        download_url = requests.compat.urljoin(report_url, download_link)
        print(f"[food_safety_market_ntpe] Download stall ODS: {download_url}")
        response = session.get(
            download_url,
            headers={"Referer": report_url},
            timeout=60,
        )
        response.raise_for_status()
        if not zipfile.is_zipfile(io.BytesIO(response.content)):
            raise ValueError(
                "Downloaded New Taipei market stall file is not a valid ODS file "
                f"for report year {report_year}."
            )
        return response.content

    def _parse_stall_ods(ods_content):
        """解析 ODS content.xml，整理各市場攤位類別欄位。"""
        ns = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
            "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        }
        districts = ["板橋", "三重", "中和", "永和", "新莊", "新店", "土城", "蘆洲", "樹林", 
                     "鶯歌", "三峽", "淡水", "汐止", "瑞芳", "五股", "泰山", "林口", "深坑", 
                     "石碇", "坪林", "三芝", "石門", "八里", "平溪", "雙溪", "貢寮", "金山", 
                     "萬里", "烏來",]

        def split_market_name(full_name):
            """把 ODS 的市場全名拆成行政區與市場名稱。"""
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
        result = pd.DataFrame(rows)
        print(f"[food_safety_market_ntpe] Parsed stall rows: {len(result)}")
        return result

    def _normalize_market_name(name):
        """移除市場名稱常見詞，供名冊與 ODS 資料比對。"""
        normalized = str(name).strip()
        for token in ["公有零售市場", "公有市場", "零售市場", "公有", "零售", "市場", "2樓"]:
            normalized = normalized.replace(token, "")
        return normalized.strip()

    def _geocode_with_tpgos(addresses):
        """用 TPgOS 批次地址轉座標；失敗時回傳空結果讓下一階段接手。"""
        if addresses.empty:
            print("[food_safety_market_ntpe] Skip TPgOS geocoding: no addresses")
            return pd.DataFrame(
                columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
            )

        print(f"[food_safety_market_ntpe] TPgOS geocoding addresses: {len(addresses)}")
        try:
            lng, lat = get_addr_xy_parallel(addresses, sleep_time=0.5)
        except Exception as error:
            print(f"Skip TPgOS geocoding: {error}")
            return pd.DataFrame(
                columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
            )

        result = pd.DataFrame(
            {"geocoding_address": addresses, "tpgos_lng": lng, "tpgos_lat": lat}
        )
        print(
            "[food_safety_market_ntpe] TPgOS geocoded: "
            f"{result['tpgos_lng'].notna().sum()}/{len(result)}"
        )
        return result

    def _geocode_with_nominatim(addresses):
        """用 Nominatim 補定位 TPgOS 未命中的地址。"""
        if addresses.empty:
            print("[food_safety_market_ntpe] Skip Nominatim geocoding: no addresses")
            return pd.DataFrame(
                columns=[
                    "geocoding_address",
                    "osm_lng",
                    "osm_lat",
                    "osm_query",
                    "osm_display_name",
                    "osm_location_method",
                ]
            )

        print(
            "[food_safety_market_ntpe] Nominatim geocoding addresses: "
            f"{len(addresses)}"
        )
        try:
            from utils.nominatim_geocoder import geocode_addresses_with_osm

            result = geocode_addresses_with_osm(addresses).rename(
                columns={"address": "geocoding_address"}
            )
            print(
                "[food_safety_market_ntpe] Nominatim geocoded: "
                f"{result['osm_lng'].notna().sum()}/{len(result)}"
            )
            return result
        except ImportError as error:
            print(f"Skip Nominatim geocoding import: {error}")
        except Exception as error:
            print(f"Skip Nominatim geocoding: {error}")

        return pd.DataFrame(
            columns=[
                "geocoding_address",
                "osm_lng",
                "osm_lat",
                "osm_query",
                "osm_display_name",
                "osm_location_method",
            ]
        )

    print("[food_safety_market_ntpe] Start ETL")
    print("[food_safety_market_ntpe] Fetch New Taipei market list")
    client = NewTaipeiAPIClient(rid, input_format="json")
    raw_data = pd.DataFrame(client.get_all_data(size=1000))
    print(f"[food_safety_market_ntpe] Raw market rows: {len(raw_data)}")

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
    print(
        "[food_safety_market_ntpe] Market rows matched with stall data: "
        f"{data['stall_total'].notna().sum()}/{len(data)}"
    )
    for col in stall_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    print("[food_safety_market_ntpe] Normalize addresses")
    addr = data["address"]
    addr_cleaned = clean_data(addr)
    standard_addr_list = main_process(addr_cleaned)
    _, output = save_data(addr, addr_cleaned, standard_addr_list)
    data["address"] = output
    data["geocoding_address"] = data["address"]

    # 定位順序參考 component6 新北市做法：TPgOS、Nominatim、行政區中心。
    tpgos_addresses = pd.Series(data["geocoding_address"].dropna().unique())
    tpgos_geocoded = _geocode_with_tpgos(tpgos_addresses)
    data = data.merge(tpgos_geocoded, on="geocoding_address", how="left")

    missing_addresses = pd.Series(
        data.loc[data["tpgos_lng"].isna(), "geocoding_address"].dropna().unique()
    )
    osm_geocoded = _geocode_with_nominatim(missing_addresses)
    data = data.merge(osm_geocoded, on="geocoding_address", how="left")
    data["lng"] = data["tpgos_lng"].combine_first(data["osm_lng"])
    data["lat"] = data["tpgos_lat"].combine_first(data["osm_lat"])
    data["location_method"] = "OpenStreetMap道路/地名定位"
    data.loc[data["tpgos_lng"].notna(), "location_method"] = "地址轉座標"

    missing = data["lng"].isna() | data["lat"].isna()
    for index, row in data.loc[missing].iterrows():
        centroid = DISTRICT_CENTROIDS.get(f"{row['city']}{row['district']}")
        if centroid:
            data.loc[index, "lng"] = centroid[0]
            data.loc[index, "lat"] = centroid[1]
            data.loc[index, "location_method"] = "行政區中心"
    print(
        "[food_safety_market_ntpe] District centroid fallback rows: "
        f"{(data['location_method'] == '行政區中心').sum()}"
    )

    if data["lng"].isna().any() or data["lat"].isna().any():
        raise ValueError("Some New Taipei market records were not geocoded.")
    print(f"[food_safety_market_ntpe] Geocoded market rows: {len(data)}")

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
    print(f"[food_safety_market_ntpe] Ready rows to save: {len(ready_data)}")

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
    print("[food_safety_market_ntpe] ETL finished")


dag = CommonDag(
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="food_safety_market_ntpe",
)
dag.create_dag(etl_func=_transfer)
