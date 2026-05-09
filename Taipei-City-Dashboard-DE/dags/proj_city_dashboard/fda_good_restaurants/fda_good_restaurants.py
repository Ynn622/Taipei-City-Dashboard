from airflow import DAG
from operators.common_pipeline import CommonDag


NTPC_ZONES = ["萬里區", "金山區", "板橋區", "汐止區", "深坑區", "石碇區", "瑞芳區", "平溪區", "雙溪區", "貢寮區", 
              "新店區", "坪林區", "烏來區", "永和區", "中和區", "土城區", "三峽區", "樹林區", "鶯歌區", "三重區", 
              "新莊區", "泰山區", "林口區", "蘆洲區", "五股區", "八里區", "淡水區", "三芝區", "石門區", ]

NTPC_AWARD_URL = "https://foodtracer.health.ntpc.gov.tw/FoodMap/GetFoodAwardMarkers"
TPE_AWARD_URL = (
    "https://data.taipei/api/dataset/59579c19-a561-4564-8c0f-545bfb32c0f6/"
    "resource/c5646d80-9118-4439-b924-075f96371d75/download"
)


def _fda_good_restaurants(**kwargs):
    import datetime
    import re
    from io import BytesIO

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.get_time import get_tpe_now_time_str
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df
    from utils.transform_time import convert_str_to_time_format

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")
    geometry_type = "Point"
    from_crs = 4326

    def normalize_address(address, city):
        """整理來源地址格式，並補上縣市前綴。"""
        address = "" if pd.isna(address) else str(address).strip()
        address = address.replace("台北市", "臺北市")
        address = re.sub(r"\s+", "", address)
        if city and address and not address.startswith(city):
            address = f"{city}{address}"
        address = re.sub(r"^(臺北市[^區]+區)臺北市[^區]+區", r"\1", address)
        address = re.sub(r"^(新北市[^區]+區)新北市[^區]+區", r"\1", address)
        return address

    def parse_award(text):
        """從標章文字中解析民國年度與評核結果。"""
        if not text:
            return None, None
        text = str(text)
        match = re.search(r"(?P<year>\d{3})\s*年度\s*(?P<rating>[優良])\s*級?", text)
        if not match:
            match = re.search(r"(?P<year>\d{3}).*?(?P<rating>[優良])標章", text)
        if not match:
            return None, None
        return int(match.group("year")), match.group("rating")

    def parse_ntpc_latest_award(row):
        """從新北 API 的標章資訊找出最新年度與評核結果。"""
        candidates = []
        for key in ["Name", "url"]:
            year, rating = parse_award(row.get(key))
            if year and rating:
                candidates.append((year, rating))
        for item in row.get("imgList") or []:
            for key in ["Name", "Path"]:
                year, rating = parse_award(item.get(key))
                if year and rating:
                    candidates.append((year, rating))
        if not candidates:
            return None, None
        return max(candidates, key=lambda item: item[0])

    def get_roc_year():
        """取得台北時區的當前民國年，作為備用年度。"""
        taipei_timezone = datetime.timezone(datetime.timedelta(hours=8))
        return datetime.datetime.now(taipei_timezone).year - 1911

    def fill_missing_coordinates(coordinates, geocoded, lng_col, lat_col):
        """用單一 geocoding 結果補齊缺漏的經緯度。"""
        if geocoded.empty:
            return coordinates

        fallback = geocoded[["address", lng_col, lat_col]].rename(
            columns={lng_col: "fallback_lng", lat_col: "fallback_lat"}
        )
        coordinates = pd.merge(coordinates, fallback, on="address", how="left")
        coordinates["lng"] = coordinates["lng"].fillna(coordinates["fallback_lng"])
        coordinates["lat"] = coordinates["lat"].fillna(coordinates["fallback_lat"])
        return coordinates.drop(columns=["fallback_lng", "fallback_lat"])

    def get_missing_addresses(coordinates):
        """取出尚未取得經緯度的不重複地址。"""
        return pd.Series(
            coordinates.loc[
                coordinates["lng"].isna() | coordinates["lat"].isna(), "address"
            ].dropna().unique()
        )

    def geocode_with_taipei_house_numbers(coordinates):
        """優先使用臺北市門牌位置資料做門牌級定位。"""
        missing_addresses = get_missing_addresses(coordinates)
        if missing_addresses.empty:
            return coordinates

        try:
            from utils.taipei_address_geocoder import (
                geocode_taipei_addresses_with_house_number_dataset,
            )
            geocoded = geocode_taipei_addresses_with_house_number_dataset(
                missing_addresses
            )
        except ImportError as error:
            print(f"Skip Taipei house number geocoding import: {error}")
            return coordinates
        except Exception as error:
            print(f"Skip Taipei house number geocoding: {error}")
            return coordinates

        return fill_missing_coordinates(
            coordinates, geocoded, "taipei_house_lng", "taipei_house_lat"
        )

    def geocode_with_tpgos(coordinates):
        """使用專案既有 TPGOS 地址轉座標作為第二順位。"""
        missing_addresses = get_missing_addresses(coordinates)
        if missing_addresses.empty:
            return coordinates

        try:
            from utils.transform_address import get_addr_xy_parallel
            fallback_lng, fallback_lat = get_addr_xy_parallel(
                missing_addresses, sleep_time=0.5
            )
        except ImportError as error:
            print(f"Skip TPGOS geocoding import: {error}")
            return coordinates
        except Exception as error:
            print(f"Skip TPGOS geocoding: {error}")
            return coordinates

        geocoded = pd.DataFrame(
            {
                "address": missing_addresses,
                "tpgos_lng": fallback_lng,
                "tpgos_lat": fallback_lat,
            }
        )
        return fill_missing_coordinates(coordinates, geocoded, "tpgos_lng", "tpgos_lat")

    def geocode_with_nominatim(coordinates):
        """使用 Nominatim 作為道路或地名層級的最後定位備援。"""
        missing_addresses = get_missing_addresses(coordinates)
        if missing_addresses.empty:
            return coordinates

        try:
            from utils.nominatim_geocoder import geocode_addresses_with_nominatim
            geocoded = geocode_addresses_with_nominatim(missing_addresses)
        except ImportError as error:
            print(f"Skip Nominatim geocoding import: {error}")
            return coordinates
        except Exception as error:
            print(f"Skip Nominatim geocoding: {error}")
            return coordinates

        return fill_missing_coordinates(coordinates, geocoded, "lng", "lat")

    def geocode_addresses(addresses):
        """依優先順序轉換臺北市地址，無法定位者保留空值。"""
        coordinates = pd.DataFrame(
            {
                "address": pd.Series(addresses)
                .dropna()
                .astype(str)
                .drop_duplicates()
                .reset_index(drop=True)
            }
        )
        coordinates["lng"] = None
        coordinates["lat"] = None
        coordinates = geocode_with_taipei_house_numbers(coordinates)
        coordinates = geocode_with_tpgos(coordinates)
        coordinates = geocode_with_nominatim(coordinates)
        return coordinates[["address", "lng", "lat"]]

    def extract_ntpc_data():
        """取得新北市標章資料，並使用來源 API 提供的座標。"""
        response = requests.post(
            NTPC_AWARD_URL,
            data={"ZoneID": ",".join(NTPC_ZONES)},
            timeout=60,
            verify=False,
        )
        response.raise_for_status()
        raw_data = response.json()
        rows = []
        for item in raw_data:
            award_year, rating_result = parse_ntpc_latest_award(item)
            if rating_result not in {"優", "良"}:
                continue
            address = normalize_address(item.get("Address"), "新北市")
            rows.append(
                {
                    "city": "新北市",
                    "district": address[3:6],
                    "award_year": award_year,
                    "restaurant_name": item.get("label"),
                    "address": address,
                    "rating_result": rating_result,
                    "lng": item.get("lon"),
                    "lat": item.get("lat"),
                }
            )
        data = pd.DataFrame(rows)
        if data.empty:
            return data
        data["award_year"] = pd.to_numeric(data["award_year"], errors="coerce")
        data["lng"] = pd.to_numeric(data["lng"], errors="coerce")
        data["lat"] = pd.to_numeric(data["lat"], errors="coerce")
        data = data.dropna(subset=["award_year", "lng", "lat"])
        data["award_year"] = data["award_year"].astype(int)
        return data.drop_duplicates(
            subset=["city", "award_year", "restaurant_name", "address", "rating_result"]
        )

    def extract_tpe_data(award_year):
        """取得臺北市標章 CSV，並用地址轉座標補上經緯度。"""
        response = requests.get(TPE_AWARD_URL, timeout=60)
        response.raise_for_status()
        raw_data = pd.read_csv(BytesIO(response.content), encoding="utf-8-sig")
        data = raw_data.rename(
            columns={
                "業者名稱店名": "restaurant_name",
                "地址": "address",
                "評核結果": "rating_result",
            }
        )
        data = data[["restaurant_name", "address", "rating_result"]].copy()
        data = data[data["rating_result"].isin(["優", "良"])]
        data["city"] = "臺北市"
        data["address"] = data["address"].apply(
            lambda value: normalize_address(value, "臺北市")
        )
        data = data.dropna(subset=["restaurant_name", "address"])
        data = data.drop_duplicates(subset=["restaurant_name", "address", "rating_result"])

        coord_data = geocode_addresses(pd.Series(data["address"].dropna().unique()))
        data = pd.merge(data, coord_data, on="address", how="left")

        data["district"] = data["address"].str.extract(
            r"(中正區|大同區|中山區|松山區|大安區|萬華區|信義區|士林區|北投區|內湖區|南港區|文山區)",
            expand=False,
        )
        data["award_year"] = award_year
        data["lng"] = pd.to_numeric(data["lng"], errors="coerce")
        data["lat"] = pd.to_numeric(data["lat"], errors="coerce")
        return data.dropna(subset=["lng", "lat"])

    ntpc_data = extract_ntpc_data()
    source_latest_year = (
        int(ntpc_data["award_year"].max()) if not ntpc_data.empty else get_roc_year()
    )
    tpe_data = extract_tpe_data(source_latest_year)
    data = pd.concat([ntpc_data, tpe_data], ignore_index=True)
    if data.empty:
        raise ValueError("No good restaurant award data was extracted.")

    latest_year = int(data["award_year"].max())
    data = data[data["award_year"] == latest_year].copy()
    data["data_time"] = get_tpe_now_time_str(is_with_tz=True)
    data["data_time"] = convert_str_to_time_format(data["data_time"])

    gdata = add_point_wkbgeometry_column_to_df(
        data, data["lng"], data["lat"], from_crs=from_crs
    )
    ready_data = gdata[
        [
            "data_time",
            "city",
            "district",
            "award_year",
            "restaurant_name",
            "address",
            "lng",
            "lat",
            "rating_result",
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
    update_lasttime_in_data_to_dataset_info(
        engine,
        airflow_dag_id=f"proj_city_dashboard_{dag_id}",
        lasttime_in_data=ready_data["data_time"].max(),
    )


dag = CommonDag(proj_folder="proj_city_dashboard", dag_folder="fda_good_restaurants")
dag.create_dag(etl_func=_fda_good_restaurants)
