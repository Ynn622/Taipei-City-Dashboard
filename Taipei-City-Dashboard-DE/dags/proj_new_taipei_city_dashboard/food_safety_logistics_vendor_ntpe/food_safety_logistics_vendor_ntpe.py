from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.fda_food_vendor import (
        fetch_vendor_records,
        jitter_coordinate,
        normalize_address_for_geocoding,
        vendor_records_to_points,
    )
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.nominatim_geocoder import geocode_addresses_with_osm
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

    _, records = fetch_vendor_records("新北市", vendor_category_code="6")
    fallback_points = vendor_records_to_points(records)

    records["geocoding_address"] = records["address"].apply(
        normalize_address_for_geocoding
    )
    unique_addresses = pd.Series(records["geocoding_address"].dropna().unique())
    lng, lat = get_addr_xy_parallel(unique_addresses, sleep_time=0.5)
    geocoded = pd.DataFrame(
        {"geocoding_address": unique_addresses, "tpgos_lng": lng, "tpgos_lat": lat}
    )
    data = records.merge(geocoded, on="geocoding_address", how="left")

    missing_addresses = data.loc[data["tpgos_lng"].isna(), "address"]
    osm_geocoded = geocode_addresses_with_osm(missing_addresses)
    data = data.merge(osm_geocoded, on="address", how="left")
    data = data.merge(
        fallback_points[["source_row_no", "lng", "lat"]].rename(
            columns={"lng": "fallback_lng", "lat": "fallback_lat"}
        ),
        on="source_row_no",
        how="left",
    )
    data["lng"] = data["tpgos_lng"].combine_first(data["osm_lng"])
    data["lat"] = data["tpgos_lat"].combine_first(data["osm_lat"])
    data["location_method"] = "行政區中心微偏移"
    data.loc[data["osm_lng"].notna() & data["tpgos_lng"].isna(), "location_method"] = (
        data["osm_location_method"]
    )
    data.loc[data["tpgos_lng"].notna(), "location_method"] = "地址轉座標"

    osm_mask = data["tpgos_lng"].isna() & data["osm_lng"].notna()
    for index, row in data.loc[osm_mask].iterrows():
        data.loc[index, ["lng", "lat"]] = jitter_coordinate(
            row["lng"],
            row["lat"],
            f"{row.get('registration_no')}|{row.get('address')}|{row.get('source_row_no')}",
        )

    data["lng"] = data["lng"].fillna(data["fallback_lng"])
    data["lat"] = data["lat"].fillna(data["fallback_lat"])
    data["point_type"] = "業者點位"
    data = data.drop(
        columns=[
            "fallback_lng",
            "fallback_lat",
            "tpgos_lng",
            "tpgos_lat",
            "osm_lng",
            "osm_lat",
        ]
    )
    data["data_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime("%Y-%m-%d %H:%M:%S")
    lasttime_in_data = data["data_time"].max()

    if data.empty:
        raise ValueError("No New Taipei FDA logistics vendor records were aggregated.")

    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=from_crs,
    )
    ready_data = gdata[
        [
            "data_time",
            "city",
            "normalized_city",
            "district",
            "vendor_category_code",
            "vendor_category",
            "source_row_no",
            "registration_item",
            "registration_no",
            "name",
            "address",
            "geocoding_address",
            "company_registration_name",
            "source_page",
            "point_type",
            "location_method",
            "osm_query",
            "osm_display_name",
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
    dag_folder="food_safety_logistics_vendor_ntpe",
)
dag.create_dag(etl_func=_transfer)
