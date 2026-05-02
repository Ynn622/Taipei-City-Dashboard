from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.extract_stage import get_current_rid_from_page_id, get_data_taipei_api
    from utils.fda_food_vendor import (
        DISTRICT_CENTROIDS,
        extract_district,
        geocode_addresses_with_osm,
        geocode_taipei_addresses_with_house_number_dataset,
        jitter_coordinate,
    )
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

    page_id = "32aea2da-14a7-47b6-a687-57e29c1ad4a7"
    from_crs = 4326
    geometry_type = "Point"

    def _infer_taipei_district(address):
        district = extract_district(address)
        if district:
            return district
        text = str(address)
        road_to_district = {
            "平菁街": "士林區",
            "碧山路": "內湖區",
            "指南路": "文山區",
        }
        for road, district in road_to_district.items():
            if road in text:
                return district
        return ""

    rid = get_current_rid_from_page_id(page_id)
    raw_data = pd.DataFrame(get_data_taipei_api(rid))
    raw_data = raw_data[raw_data["農場名稱"].fillna("").astype(str).str.strip() != ""]
    raw_data["data_time"] = raw_data["_importdate"].apply(lambda item: item["date"])
    lasttime_in_data = raw_data["data_time"].max()

    data = raw_data.rename(
        columns={
            "編號": "source_row_no",
            "農場名稱": "name",
            "農友姓名": "operator",
            "通訊地址": "address",
            "認證字號": "certification_no",
            "面積（公頃）": "area_ha",
            "食農教育體驗": "food_education",
            "飼養蜜蜂": "beekeeping",
            "飼養雞隻": "chicken_raising",
            "備註": "note",
        }
    )
    data = data.drop(columns=["_id", "_importdate"], errors="ignore")
    data["city"] = "臺北市"
    data["source_dataset"] = "臺北市有機農場"
    data["source_url"] = (
        "https://data.taipei/dataset/detail?id=32aea2da-14a7-47b6-a687-57e29c1ad4a7"
    )
    data["source_type"] = "有機農場"
    data["certification_status"] = "有機"

    for col in ["name", "operator", "address", "certification_no"]:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["district"] = data["address"].apply(_infer_taipei_district)
    data["geocoding_address"] = data["address"].where(
        data["address"].str.startswith("臺北市"),
        data["city"] + data["district"] + data["address"],
    )
    data["area_ha"] = pd.to_numeric(data["area_ha"], errors="coerce")

    house_geocoded = geocode_taipei_addresses_with_house_number_dataset(
        data["geocoding_address"]
    ).rename(columns={"address": "geocoding_address"})
    data = data.merge(house_geocoded, on="geocoding_address", how="left")
    missing_addresses = data.loc[data["taipei_house_lng"].isna(), "geocoding_address"]
    osm_geocoded = geocode_addresses_with_osm(missing_addresses).rename(
        columns={"address": "geocoding_address"}
    )
    data = data.merge(osm_geocoded, on="geocoding_address", how="left")

    data["lng"] = data["taipei_house_lng"].combine_first(data["osm_lng"])
    data["lat"] = data["taipei_house_lat"].combine_first(data["osm_lat"])
    data["location_method"] = data["taipei_house_location_method"].where(
        data["taipei_house_lng"].notna(),
        data["osm_location_method"],
    )

    missing = data["lng"].isna() | data["lat"].isna()
    for index, row in data.loc[missing].iterrows():
        centroid = DISTRICT_CENTROIDS.get(f"{row['city']}{row['district']}")
        if centroid:
            lng, lat = jitter_coordinate(centroid[0], centroid[1], row["source_row_no"])
            data.loc[index, "lng"] = lng
            data.loc[index, "lat"] = lat
            data.loc[index, "location_method"] = "行政區中心"

    if data["lng"].isna().any() or data["lat"].isna().any():
        raise ValueError("Some Taipei food source records were not geocoded.")

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
            "operator",
            "city",
            "district",
            "address",
            "certification_no",
            "certification_status",
            "area_ha",
            "food_education",
            "beekeeping",
            "chicken_raising",
            "note",
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
    proj_folder="proj_city_dashboard",
    dag_folder="food_source_tpe",
)
dag.create_dag(etl_func=_transfer)
