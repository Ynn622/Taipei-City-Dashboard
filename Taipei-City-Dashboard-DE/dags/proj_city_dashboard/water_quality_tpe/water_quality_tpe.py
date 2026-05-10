from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    from io import BytesIO

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

    source_url = (
        "https://tsis.dbas.gov.taipei/statis/webMain.aspx?"
        "sys=220&ymf=10600&kind=21&type=0&funid=a05021902&cycle=4&"
        "outmode=12&compmode=0&outkind=3&deflst=2&nzo=1"
    )
    source_dataset_url = (
        "https://data.taipei/dataset/detail?id=9626c65d-8fe7-45bb-bbe2-7439bed81010"
    )
    plant_locations = {
        "直潭淨水場": (121.5265584, 24.9428717, "新店區"),
        "長興淨水場": (121.5452213, 25.0142391, "文山區"),
        "公館淨水場": (121.5320, 25.0140, "中正區"),
        "雙溪淨水場": (121.5690369, 25.1143633, "士林區"),
        "陽明淨水場": (121.5316063, 25.1510961, "北投區"),
    }

    def to_float(value):
        number = pd.to_numeric(value, errors="coerce")
        return None if pd.isna(number) else float(number)

    response = requests.get(
        source_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    raw = pd.read_csv(BytesIO(response.content), encoding="utf-8-sig")
    latest_period = raw["統計期"].max()
    latest = raw[raw["統計期"] == latest_period].copy()

    records = []
    for index, (plant_name, group) in enumerate(latest.groupby("淨水場別"), start=1):
        lng, lat, district = plant_locations[plant_name]
        records.append(
            {
                "source_row_no": index,
                "name": plant_name,
                "english_name": "",
                "city": "臺北市",
                "district": district,
                "address": "",
                "water_sources": "、".join(group["自來水水源別"].astype(str).unique()),
                "data_time": latest_period,
                "qualified": "年度均值",
                "ph": round(group["PH數值"].map(to_float).mean(), 2),
                "turbidity_ntu": round(
                    group["濁度數值[散射濁度單位]"].map(to_float).mean(), 2
                ),
                "free_residual_chlorine_mg_l": round(
                    group["自由有效餘氯數值[mg/L]"].map(to_float).mean(), 2
                ),
                "total_hardness_mg_l": round(
                    group["總硬度數值[mg/L]"].map(to_float).mean(), 1
                ),
                "total_dissolved_solids_mg_l": round(
                    group["總溶解固體量[mg/L]"].map(to_float).mean(), 1
                ),
                "coliform_cfu_100ml": "、".join(
                    group["大腸桿菌群數[每百毫升菌落數]"].astype(str).unique()
                ),
                "source_dataset": "臺北自來水水質檢驗(淨水場清水水質)",
                "source_url": source_dataset_url,
                "location_method": "固定淨水場座標",
                "lng": lng,
                "lat": lat,
            }
        )
    data = pd.DataFrame(records)
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
    proj_folder="proj_city_dashboard",
    dag_folder="water_quality_tpe",
)
dag.create_dag(etl_func=_transfer)
