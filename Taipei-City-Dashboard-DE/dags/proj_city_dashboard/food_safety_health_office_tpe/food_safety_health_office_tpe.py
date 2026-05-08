from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.fda_food_vendor import (
        geocode_addresses_with_osm,
        geocode_taipei_addresses_with_house_number_dataset,
    )
    from utils.health_office import fetch_taipei_health_centers
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

    from_crs = 4326
    geometry_type = "Point"

    data = fetch_taipei_health_centers()
    data["geocoding_address"] = data["address"]

    house_geocoded = geocode_taipei_addresses_with_house_number_dataset(data["address"])
    data = data.merge(house_geocoded, on="address", how="left")

    tpgos_addresses = pd.Series(
        data.loc[data["taipei_house_lng"].isna(), "geocoding_address"].dropna().unique()
    )
    if tpgos_addresses.empty:
        tpgos_geocoded = pd.DataFrame(
            columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
        )
    else:
        lng, lat = get_addr_xy_parallel(tpgos_addresses, sleep_time=0.5)
        tpgos_geocoded = pd.DataFrame(
            {"geocoding_address": tpgos_addresses, "tpgos_lng": lng, "tpgos_lat": lat}
        )
    data = data.merge(tpgos_geocoded, on="geocoding_address", how="left")

    missing_addresses = data.loc[
        data["taipei_house_lng"].isna() & data["tpgos_lng"].isna(), "address"
    ]
    osm_geocoded = geocode_addresses_with_osm(missing_addresses)
    data = data.merge(osm_geocoded, on="address", how="left")

    data["lng"] = (
        data["taipei_house_lng"]
        .combine_first(data["tpgos_lng"])
        .combine_first(data["osm_lng"])
    )
    data["lat"] = (
        data["taipei_house_lat"]
        .combine_first(data["tpgos_lat"])
        .combine_first(data["osm_lat"])
    )
    data["location_method"] = "OpenStreetMap道路/地名定位"
    data.loc[data["tpgos_lng"].notna(), "location_method"] = "地址轉座標"
    data.loc[data["taipei_house_lng"].notna(), "location_method"] = data[
        "taipei_house_location_method"
    ]
    data["data_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime("%Y-%m-%d %H:%M:%S")
    lasttime_in_data = data["data_time"].max()

    if data["lng"].isna().any() or data["lat"].isna().any():
        raise ValueError("Some Taipei health centers were not geocoded.")

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
            "district_code",
            "agency_type",
            "address",
            "phone",
            "website",
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
    proj_folder="proj_city_dashboard",
    dag_folder="food_safety_health_office_tpe",
)
dag.create_dag(etl_func=_transfer)
