from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import io
    import re

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
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

    page_id = "09a917a0-0fb5-47e1-957c-5f1268fba517"
    dataset_url = f"https://data.taipei/dataset/detail?id={page_id}"
    from_crs = 4326
    geometry_type = "Point"

    def _discover_resource_urls():
        response = requests.get(dataset_url, timeout=60)
        response.raise_for_status()
        resource_ids = list(
            dict.fromkeys(
                re.findall(
                    rf"/api/dataset/{page_id}/resource/([^/]+)/download",
                    response.text,
                )
            )
        )
        if not resource_ids:
            raise ValueError("No Taipei food audit violation resources found.")
        return [
            f"https://data.taipei/api/dataset/{page_id}/resource/{rid}/download"
            for rid in resource_ids
        ]

    taipei_districts = {
        key.replace("臺北市", "")
        for key in DISTRICT_CENTROIDS
        if key.startswith("臺北市")
    }

    def _split_store_and_address(value):
        text = str(value or "").strip()
        if "/" in text:
            name, address = text.rsplit("/", 1)
            if address.strip().startswith(("臺北市", "台北市")):
                return name.strip(), address.strip()
        address_match = re.search(r"(臺北市|台北市).+$", text)
        if address_match:
            return text[: address_match.start()].strip(), address_match.group(0).strip()
        return text, text

    frames = []
    for resource_url in _discover_resource_urls():
        response = requests.get(resource_url, timeout=120)
        response.raise_for_status()
        frame = pd.read_csv(io.BytesIO(response.content), dtype=str)
        frame["source_url"] = resource_url
        frames.append(frame)

    raw_data = pd.concat(frames, ignore_index=True).dropna(how="all")
    raw_data = raw_data[
        raw_data["抽驗地點"].fillna("").astype(str).str.strip() != ""
    ].copy()

    split_values = raw_data["抽驗地點"].apply(_split_store_and_address)
    data = pd.DataFrame(
        {
            "project_name": raw_data.get("專案名稱", ""),
            "sample_date": raw_data.get("抽驗日期", ""),
            "product_category": raw_data.get("分類", ""),
            "sample_item": raw_data.get("檢體名稱", ""),
            "postal_code": raw_data.get("抽驗行政郵遞區號", ""),
            "name": split_values.apply(lambda item: item[0]),
            "address": split_values.apply(lambda item: item[1]),
            "inspection_result": raw_data.get("檢驗結果", ""),
            "violation_reason": raw_data.get("不符合規定原因", ""),
            "source_url": raw_data["source_url"],
        }
    ).fillna("")

    for col in data.columns:
        data[col] = data[col].astype(str).str.strip()

    data = data[
        data["inspection_result"].str.contains("不符合|不合格", na=False)
    ].copy()
    data.insert(0, "source_row_no", range(1, len(data) + 1))
    data["city"] = "臺北市"
    data["source_dataset"] = "臺北市衛生局食品抽驗不合格清冊"
    data["source_type"] = "食品抽驗不合格"
    data["district"] = data["address"].apply(extract_district)
    data = data[data["district"].isin(taipei_districts)].copy()
    data["geocoding_address"] = data["address"].where(
        data["address"].str.startswith(("臺北市", "台北市")),
        data["city"] + data["district"] + data["address"],
    )
    data["data_time"] = pd.to_datetime(
        data["sample_date"],
        format="%Y%m%d",
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")
    lasttime_in_data = data["data_time"].dropna().max()

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
        raise ValueError("Some Taipei food audit violation records were not geocoded.")

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
            "postal_code",
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
    dag_folder="food_audit_violation_tpe",
)
dag.create_dag(etl_func=_transfer)
