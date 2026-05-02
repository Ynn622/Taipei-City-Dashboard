from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import pandas as pd
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
