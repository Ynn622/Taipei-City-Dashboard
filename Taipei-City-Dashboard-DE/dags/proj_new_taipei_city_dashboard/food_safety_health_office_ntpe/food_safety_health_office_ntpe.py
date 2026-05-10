from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    """抓取新北衛生所資料、定位後寫入 ready data table。"""
    from io import BytesIO

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.district_geocoder import DISTRICT_CENTROIDS
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    new_taipei_health_office_url = (
        "https://data.ntpc.gov.tw/api/datasets/"
        "2553bb1a-bcbb-4284-8b24-acfefe966f1e/csv/file"
    )

    def read_csv_from_url(url, encoding):
        """從指定 URL 下載 CSV 並轉成 DataFrame。"""
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
        return pd.read_csv(BytesIO(response.content), encoding=encoding)

    def fetch_new_taipei_health_offices():
        """下載並標準化新北市衛生所資料。"""
        raw = read_csv_from_url(new_taipei_health_office_url, encoding="utf-8-sig")
        data = raw.rename(
            columns={
                "seqno": "source_row_no",
                "hosp_id": "office_id",
                "hosp_name": "name",
                "tel": "phone",
                "hosp_addr": "address",
                "open time": "open_time",
            }
        )
        data["city"] = "新北市"
        data["agency_type"] = "衛生所"
        data["website"] = ""
        data["source_dataset"] = "新北市各區衛生所"
        data["source_url"] = "https://data.gov.tw/dataset/125693"
        result = data[
            [
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
            ]
        ].fillna("")

        # 開放資料不含衛生局本體，手動補入主責機關點位。
        main_bureau = pd.DataFrame(
            [
                {
                    "source_row_no": len(result) + 1,
                    "office_id": "",
                    "name": "新北市政府衛生局",
                    "city": "新北市",
                    "district": "板橋區",
                    "agency_type": "衛生局",
                    "address": "新北市板橋區英士路192-1號",
                    "phone": "(02)22577155",
                    "extension": "",
                    "zipcode": "220",
                    "open_time": "",
                    "website": "https://www.health.ntpc.gov.tw/",
                    "source_dataset": "新北市政府衛生局",
                    "source_url": "https://www.health.ntpc.gov.tw/",
                }
            ]
        )
        return pd.concat([result, main_bureau], ignore_index=True).fillna("")

    def geocode_with_tpgos(addresses):
        """用 TPgOS 地址轉座標，失敗時回傳空結果讓後續定位接手。"""
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
        """用 Nominatim 定位，失敗時回傳空結果讓行政區中心接手。"""
        if addresses.empty:
            return pd.DataFrame(
                columns=[
                    "geocoding_address",
                    "osm_lng",
                    "osm_lat",
                    "osm_query",
                    "osm_display_name",
                    "osm_location_method",
                ]
            )

        try:
            from utils.nominatim_geocoder import geocode_addresses_with_osm

            return geocode_addresses_with_osm(addresses).rename(
                columns={"address": "geocoding_address"}
            )
        except ImportError as error:
            print(f"Skip Nominatim geocoding import: {error}")
        except Exception as error:
            print(f"Skip Nominatim geocoding: {error}")

        return pd.DataFrame(
            columns=[
                "geocoding_address",
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

    data = fetch_new_taipei_health_offices()
    data["geocoding_address"] = data["address"]

    # 定位順序：TPgOS、Nominatim、行政區中心。
    tpgos_addresses = pd.Series(data["geocoding_address"].dropna().unique())
    tpgos_geocoded = geocode_with_tpgos(tpgos_addresses)
    data = data.merge(tpgos_geocoded, on="geocoding_address", how="left")

    missing_addresses = data.loc[data["tpgos_lng"].isna(), "geocoding_address"]
    osm_geocoded = geocode_with_nominatim(missing_addresses)
    data = data.merge(osm_geocoded, on="geocoding_address", how="left")
    data["lng"] = data["tpgos_lng"].combine_first(data["osm_lng"])
    data["lat"] = data["tpgos_lat"].combine_first(data["osm_lat"])
    data["location_method"] = "OpenStreetMap道路/地名定位"
    data.loc[data["tpgos_lng"].notna(), "location_method"] = "地址轉座標"
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
