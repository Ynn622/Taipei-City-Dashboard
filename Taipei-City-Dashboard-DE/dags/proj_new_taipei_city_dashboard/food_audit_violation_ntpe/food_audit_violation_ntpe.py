from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
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

    from_crs = 4326
    geometry_type = "Point"
    source_url = "https://fsmc.ntpc.gov.tw/DigitalMap/PublicWebsite"
    endpoint = f"{source_url}/GetFilteredAnalysisStoresWithCoordinates"

    response = requests.post(
        endpoint,
        data={
            "DateS": "",
            "DateE": "",
            "county": "",
            "Name0": "",
            "Name1": "",
            "Name3": "",
            "AnalysisY": "1",
            "AnalysisN": "1",
        },
        headers={
            "User-Agent": "TaipeiCityDashboardPrivate/food-audit-violation",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise ValueError("New Taipei food sampling API did not return success.")

    raw_data = pd.DataFrame(payload.get("data", []))
    raw_data = raw_data.dropna(how="all")
    raw_data = raw_data[
        raw_data["抽驗結果"].fillna("").astype(str).str.contains("不合格", na=False)
    ].copy()

    data = raw_data.rename(
        columns={
            "SD_StoreID": "source_row_no",
            "業者名稱": "name",
            "行政區": "district",
            "地址": "address",
            "Longitude": "lng",
            "Latitude": "lat",
            "抽驗結果": "inspection_result",
            "抽驗日期": "sample_date",
            "檢驗項目": "sample_item",
        }
    )

    for col in [
        "source_row_no",
        "name",
        "district",
        "address",
        "inspection_result",
        "sample_date",
        "sample_item",
    ]:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["city"] = "新北市"
    data["address"] = data["address"].where(
        data["address"].str.startswith("新北市"),
        data["city"] + data["district"] + data["address"],
    )
    data["project_name"] = "食品抽驗結果"
    data["product_category"] = data["sample_item"]
    data["violation_reason"] = "食品抽驗不合格"
    data["source_type"] = "食品抽驗不合格"
    data["source_dataset"] = "新北市食品抽驗結果"
    data["source_url"] = source_url
    data["geocoding_address"] = data["address"]
    data["location_method"] = "來源網站座標"
    data["lng"] = pd.to_numeric(data["lng"], errors="coerce")
    data["lat"] = pd.to_numeric(data["lat"], errors="coerce")
    data["data_time"] = pd.to_datetime(
        data["sample_date"].str.replace(".", "", regex=False),
        format="%Y%m%d",
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")
    lasttime_in_data = data["data_time"].dropna().max()

    data = data[data["lng"].notna() & data["lat"].notna()].copy()
    if data.empty:
        raise ValueError("No geocoded New Taipei food audit violation records found.")

    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=from_crs,
    )
    ready_data = gdata[
        [
            "data_time",
            "source_row_no",
            "name",
            "city",
            "district",
            "address",
            "sample_date",
            "project_name",
            "product_category",
            "sample_item",
            "inspection_result",
            "violation_reason",
            "source_type",
            "source_dataset",
            "source_url",
            "geocoding_address",
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
        geometry_type=geometry_type,
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, lasttime_in_data)


dag = CommonDag(
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="food_audit_violation_ntpe",
)
dag.create_dag(etl_func=_transfer)
