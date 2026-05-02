from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.fda_food_vendor import DISTRICT_CENTROIDS, geocode_addresses_with_osm
    from utils.health_office import fetch_new_taipei_health_offices
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

    data = fetch_new_taipei_health_offices()
    data["geocoding_address"] = data["address"]
    osm_geocoded = geocode_addresses_with_osm(data["address"])
    data = data.merge(osm_geocoded, on="address", how="left")
    data["lng"] = data["osm_lng"]
    data["lat"] = data["osm_lat"]
    data["location_method"] = data["osm_location_method"]
    main_bureau = data["name"] == "新北市政府衛生局"
    data.loc[main_bureau, "lng"] = 121.4594425
    data.loc[main_bureau, "lat"] = 25.0238847
    data.loc[main_bureau, "location_method"] = "同址衛生所定位"

    missing = data["lng"].isna() | data["lat"].isna()
    for index, row in data.loc[missing].iterrows():
        centroid = DISTRICT_CENTROIDS.get(f"{row['city']}{row['district']}")
        if centroid:
            data.loc[index, "lng"] = centroid[0]
            data.loc[index, "lat"] = centroid[1]
            data.loc[index, "location_method"] = "行政區中心"

    data["data_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime("%Y-%m-%d %H:%M:%S")
    lasttime_in_data = data["data_time"].max()

    if data["lng"].isna().any() or data["lat"].isna().any():
        raise ValueError("Some New Taipei health offices were not geocoded.")

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
            "office_id",
            "name",
            "city",
            "district",
            "agency_type",
            "address",
            "phone",
            "extension",
            "zipcode",
            "open_time",
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
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="food_safety_health_office_ntpe",
)
dag.create_dag(etl_func=_transfer)
