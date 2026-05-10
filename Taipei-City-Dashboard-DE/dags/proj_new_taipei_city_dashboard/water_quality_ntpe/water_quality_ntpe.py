from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import html
    import re
    from urllib.parse import urljoin

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    source_url = "https://www.water.gov.tw/ch/WaterQuality?nodeId=4631"
    plant_locations = {
        "貢寮淨水場": (121.9176223, 25.0104331),
        "老梅淨水場": (121.5499077, 25.2616237),
        "林莊淨水場": (121.6125, 25.2236),
        "坪林淨水場": (121.7118, 24.9365),
        "員山淨水場": (121.8076, 25.1055),
        "板新淨水場": (121.3562688, 24.9398341),
    }
    output_columns = [
        "source_row_no",
        "name",
        "english_name",
        "city",
        "district",
        "address",
        "water_sources",
        "data_time",
        "qualified",
        "ph",
        "turbidity_ntu",
        "free_residual_chlorine_mg_l",
        "total_hardness_mg_l",
        "total_dissolved_solids_mg_l",
        "coliform_cfu_100ml",
        "source_dataset",
        "source_url",
        "location_method",
        "lng",
        "lat",
    ]

    def to_float(value):
        number = pd.to_numeric(value, errors="coerce")
        return None if pd.isna(number) else float(number)

    def clean_cell(value):
        text = re.sub(r"<[^>]+>", "", value)
        return html.unescape(text).strip()

    def extract_table_rows(page_html):
        rows = {}
        for row_html in re.findall(
            r"<tr[^>]*>(.*?)</tr>",
            page_html,
            flags=re.S | re.I,
        ):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.S | re.I)
            if len(cells) >= 3:
                rows[clean_cell(cells[0])] = clean_cell(cells[1])
        return rows

    session = requests.Session()
    list_response = session.get(
        source_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )
    list_response.raise_for_status()
    token_match = re.search(
        r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"',
        list_response.text,
    )
    if not token_match:
        raise ValueError("Unable to find water.gov.tw request verification token.")

    search_response = session.post(
        source_url,
        data={
            "__RequestVerificationToken": token_match.group(1),
            "SearchKeyword": "新北市",
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )
    search_response.raise_for_status()

    items = re.findall(
        r'<a class="perform_item" href="([^"]+)" title="([^"]+)">(.*?)</a>',
        search_response.text,
        flags=re.S | re.I,
    )
    records = []
    for index, (href, title, body) in enumerate(items, start=1):
        title = html.unescape(title).replace("—", "-")
        name_match = re.match(r"([^()]+)(?:\(([^)]+)\))?(新北市.+)", title)
        if not name_match:
            continue

        name = name_match.group(1).strip()
        english_name = (name_match.group(2) or "").strip()
        address = name_match.group(3).strip()
        district_match = re.search(r"新北市(.+?區)", address)
        district = district_match.group(1) if district_match else ""
        date_match = re.search(r"(20\d{2}/\d{2}/\d{2})", clean_cell(body))
        detail_url = urljoin(source_url, href)
        detail_response = session.get(
            detail_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=60,
        )
        detail_response.raise_for_status()
        rows = extract_table_rows(detail_response.text)
        lng, lat = plant_locations[name]

        records.append(
            {
                "source_row_no": index,
                "name": name,
                "english_name": english_name,
                "city": "新北市",
                "district": district,
                "address": address,
                "water_sources": "",
                "data_time": date_match.group(1) if date_match else "",
                "qualified": rows.get("水質合格否(Y/N)", ""),
                "ph": to_float(rows.get("pH值(－)", "")),
                "turbidity_ntu": to_float(rows.get("濁度(NTU)", "")),
                "free_residual_chlorine_mg_l": to_float(
                    rows.get("自由有效餘氯(mg/L)", "")
                ),
                "total_hardness_mg_l": to_float(rows.get("總硬度(mg/L)", "")),
                "total_dissolved_solids_mg_l": to_float(
                    rows.get("總溶解固體量(mg/L)", "")
                ),
                "coliform_cfu_100ml": rows.get("大腸桿菌群(CFU/100mL)", ""),
                "source_dataset": "臺灣自來水公司平均水質",
                "source_url": detail_url,
                "location_method": "固定淨水場座標",
                "lng": lng,
                "lat": lat,
            }
        )
    data = pd.DataFrame(records, columns=output_columns)
    data["etl_update_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    lasttime_in_data = data["etl_update_time"].max()

    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=4326,
    )
    ready_data = gdata[
        [
            "etl_update_time",
            "source_row_no",
            "name",
            "english_name",
            "city",
            "district",
            "address",
            "water_sources",
            "data_time",
            "qualified",
            "ph",
            "turbidity_ntu",
            "free_residual_chlorine_mg_l",
            "total_hardness_mg_l",
            "total_dissolved_solids_mg_l",
            "coliform_cfu_100ml",
            "source_dataset",
            "source_url",
            "location_method",
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
        geometry_type="Point",
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, lasttime_in_data)


dag = CommonDag(
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="water_quality_ntpe",
)
dag.create_dag(etl_func=_transfer)
