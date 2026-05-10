from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    from io import BytesIO

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.district_geocoder import DISTRICT_CENTROIDS
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.taipei_address_geocoder import (
        TAIPEI_DISTRICT_CODE_TO_NAME,
        geocode_taipei_addresses_with_house_number_dataset,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    taipei_health_center_url = (
        "https://data.taipei/api/dataset/d4c6d4e0-c2b4-48e3-99b4-f670d820326b/"
        "resource/1e57f3cb-7063-4db7-a263-106ab9bdf6d1/download"
    )

    def read_csv_from_url(url, encoding):
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        return pd.read_csv(BytesIO(response.content), encoding=encoding)

    def complete_taipei_address(address, district):
        text = str(address).strip().replace("　", "")
        text = text.replace("台北巿", "臺北市").replace("臺北巿", "臺北市")
        text = text.replace("台北市", "臺北市")
        if text.startswith("臺北市"):
            without_city = text[len("臺北市") :]
            if without_city.startswith(district):
                return (
                    f"臺北市{district}"
                    f"{without_city[len(district):].replace('臺北市', '')}"
                )
            return f"臺北市{district}{without_city}"
        return f"臺北市{district}{text}"

    def fetch_taipei_health_centers():
        # Download and standardize Taipei health service center rows.
        raw = read_csv_from_url(taipei_health_center_url, encoding="cp950")
        data = raw.rename(
            columns={
                "健康服務中心名稱": "name",
                "行政區": "district_code",
                "地址": "address",
                "電話": "phone",
                "網址": "website",
            }
        )
        data["district_code"] = data["district_code"].astype(str)
        data["district"] = data["district_code"].map(TAIPEI_DISTRICT_CODE_TO_NAME)
        data["city"] = "臺北市"
        data["agency_type"] = "健康服務中心"
        data["address"] = data.apply(
            lambda row: complete_taipei_address(row["address"], row["district"]),
            axis=1,
        )
        data["website"] = data["website"].astype(str).str.strip()
        data["source_dataset"] = "臺北市健康服務中心"
        data["source_url"] = "https://data.gov.tw/dataset/121146"
        data.insert(0, "source_row_no", range(1, len(data) + 1))
        result = data[
            [
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
            ]
        ].fillna("")

        # Add the main health bureau because it is not in the open dataset.
        main_bureau = pd.DataFrame(
            [
                {
                    "source_row_no": len(result) + 1,
                    "name": "臺北市政府衛生局",
                    "city": "臺北市",
                    "district": "信義區",
                    "district_code": "63000020",
                    "agency_type": "衛生局",
                    "address": "臺北市信義區市府路1號",
                    "phone": "(02)27208889",
                    "website": "https://health.gov.taipei/",
                    "source_dataset": "臺北市政府衛生局",
                    "source_url": "https://health.gov.taipei/",
                }
            ]
        )
        return pd.concat([result, main_bureau], ignore_index=True).fillna("")

    def geocode_with_tpgos(addresses):
        if addresses.empty:
            return pd.DataFrame(
                columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
            )

        try:
            from utils.transform_address import get_addr_xy_parallel

            lng, lat = get_addr_xy_parallel(addresses, sleep_time=0.5)
        except ImportError as error:
            print(f"Skip TPgOS geocoding import: {error}")
            return pd.DataFrame(
                columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
            )
        except Exception as error:
            print(f"Skip TPgOS geocoding: {error}")
            return pd.DataFrame(
                columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
            )

        return pd.DataFrame(
            {"geocoding_address": addresses, "tpgos_lng": lng, "tpgos_lat": lat}
        )

    def geocode_with_nominatim(addresses):
        if addresses.empty:
            return pd.DataFrame(
                columns=[
                    "address",
                    "osm_lng",
                    "osm_lat",
                    "osm_query",
                    "osm_display_name",
                    "osm_location_method",
                ]
            )

        try:
            from utils.nominatim_geocoder import geocode_addresses_with_osm

            return geocode_addresses_with_osm(addresses)
        except ImportError as error:
            print(f"Skip Nominatim geocoding import: {error}")
        except Exception as error:
            print(f"Skip Nominatim geocoding: {error}")

        return pd.DataFrame(
            columns=[
                "address",
                "osm_lng",
                "osm_lat",
                "osm_query",
                "osm_display_name",
                "osm_location_method",
            ]
        )

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

    # Prefer Taipei house-number data, then TPgOS, Nominatim, and district center.
    house_geocoded = geocode_taipei_addresses_with_house_number_dataset(data["address"])
    data = data.merge(house_geocoded, on="address", how="left")

    tpgos_addresses = pd.Series(
        data.loc[data["taipei_house_lng"].isna(), "geocoding_address"].dropna().unique()
    )
    tpgos_geocoded = geocode_with_tpgos(tpgos_addresses)
    data = data.merge(tpgos_geocoded, on="geocoding_address", how="left")

    missing_addresses = data.loc[
        data["taipei_house_lng"].isna() & data["tpgos_lng"].isna(), "address"
    ]
    osm_geocoded = geocode_with_nominatim(missing_addresses)
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
