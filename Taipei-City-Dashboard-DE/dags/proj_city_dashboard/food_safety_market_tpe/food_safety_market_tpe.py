from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import re
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.extract_stage import get_current_rid_from_page_id, get_data_taipei_api
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_address import get_addr_xy_parallel
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    page_id = "f490476d-d156-4492-a463-cf3405de3b55"
    market_location_csv_url = (
        "https://data.taipei/api/dataset/89bebb3a-990d-4070-bd67-631a575f6d4a/"
        "resource/35acfce1-2c4d-4c70-aa75-601cdab2b3f7/download"
    )
    from_crs = 4326
    geometry_type = "Point"

    def _normalize_market_name(name):
        normalized = "" if pd.isna(name) else str(name).strip()
        normalized = re.sub(r"\(.*?\)|（.*?）", "", normalized)
        for token in ["臺北市", "台北市", "公有", "零售", "市場", "中繼"]:
            normalized = normalized.replace(token, "")
        return normalized.strip()

    def _load_market_locations():
        location_data = pd.read_csv(market_location_csv_url, encoding="cp950")
        location_data = location_data.rename(
            columns={
                "stitle": "location_name",
                "xAddress": "location_address",
                "GTag_longitude": "source_lng",
                "GTag_latitude": "source_lat",
            }
        )
        location_data["market_key"] = location_data["location_name"].apply(
            _normalize_market_name
        )
        location_data["lng"] = pd.to_numeric(
            location_data["source_lng"], errors="coerce"
        )
        location_data["lat"] = pd.to_numeric(
            location_data["source_lat"], errors="coerce"
        )
        location_data["location_address"] = (
            location_data["location_address"].fillna("").astype(str).str.strip()
        )
        return location_data.dropna(subset=["lng", "lat"]).drop_duplicates(
            subset=["market_key"]
        )[["market_key", "location_address", "lng", "lat"]]

    rid = get_current_rid_from_page_id(page_id)
    raw_data = pd.DataFrame(get_data_taipei_api(rid))
    raw_data["data_time"] = raw_data["_importdate"].iloc[0]["date"]
    lasttime_in_data = raw_data["data_time"].max()

    data = raw_data.rename(
        columns={
            "序號": "market_id",
            "行政區": "district",
            "市場名稱": "name",
            "總計": "stall_total",
            "蔬菜（數量）": "vegetable_stalls",
            "青果（數量）": "fruit_stalls",
            "獸肉（數量）": "meat_stalls",
            "漁產（數量）": "seafood_stalls",
            "家禽（數量）": "poultry_stalls",
            "糧食（數量）": "grain_stalls",
            "花卉（數量）": "flower_stalls",
            "雜貨（數量）": "grocery_stalls",
            "百貨（數量）": "general_merchandise_stalls",
            "飲食（數量）": "food_stalls",
            "其他": "other_stalls",
        }
    )
    data = data.drop(columns=["_id", "_importdate"], errors="ignore")
    data["city"] = "臺北市"
    data["type"] = "公有零售市場"
    data["address"] = ""

    stall_cols = [
        "stall_total",
        "vegetable_stalls",
        "fruit_stalls",
        "meat_stalls",
        "seafood_stalls",
        "poultry_stalls",
        "grain_stalls",
        "flower_stalls",
        "grocery_stalls",
        "general_merchandise_stalls",
        "food_stalls",
        "other_stalls",
    ]
    for col in stall_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0).astype(int)

    data["name_for_geocoding"] = data["name"].str.replace(
        r"\(.*?\)", "", regex=True
    ).str.strip()
    data["geocode_query"] = (
        data["city"] + data["district"] + data["name_for_geocoding"]
    )
    data["market_key"] = data["name"].apply(_normalize_market_name)

    try:
        market_locations = _load_market_locations()
    except Exception as e:
        print(f"Unable to load Taipei market location CSV: {e}")
        market_locations = pd.DataFrame(
            columns=["market_key", "location_address", "lng", "lat"]
        )

    data = data.merge(market_locations, on="market_key", how="left")
    data["address"] = data["location_address"].where(
        data["location_address"].fillna("").ne(""),
        data["address"],
    )

    missing = data["lng"].isna() | data["lat"].isna()
    if missing.any():
        try:
            unique_queries = pd.Series(
                data.loc[missing, "geocode_query"].dropna().unique()
            )
            lng, lat = get_addr_xy_parallel(unique_queries, sleep_time=0.5)
            geocoded = pd.DataFrame(
                {
                    "geocode_query": unique_queries,
                    "tpgos_lng": lng,
                    "tpgos_lat": lat,
                }
            )
            data = data.merge(geocoded, on="geocode_query", how="left")
            data["lng"] = data["lng"].fillna(data["tpgos_lng"])
            data["lat"] = data["lat"].fillna(data["tpgos_lat"])
        except Exception as e:
            print(f"Unable to geocode missing Taipei markets with TPGOS: {e}")

    data = data.dropna(subset=["lng", "lat"])
    if data.empty:
        raise ValueError("No Taipei market records were geocoded successfully.")

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
            "city",
            "district",
            "name",
            "type",
            "address",
            "stall_total",
            "vegetable_stalls",
            "fruit_stalls",
            "meat_stalls",
            "seafood_stalls",
            "poultry_stalls",
            "grain_stalls",
            "flower_stalls",
            "grocery_stalls",
            "general_merchandise_stalls",
            "food_stalls",
            "other_stalls",
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
    proj_folder="proj_city_dashboard",
    dag_folder="food_safety_market_tpe",
)
dag.create_dag(etl_func=_transfer)
