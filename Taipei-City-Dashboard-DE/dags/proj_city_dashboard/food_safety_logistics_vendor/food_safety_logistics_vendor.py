from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    """執行雙北 FDA 物流業者抓取、定位與入庫流程。"""
    import hashlib
    import math
    import re
    from io import StringIO

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.district_geocoder import (
        DISTRICT_CENTROIDS,
        extract_district,
        jitter_coordinate,
    )
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.nominatim_geocoder import geocode_addresses_with_osm
    from utils.taipei_address_geocoder import (
        geocode_taipei_addresses_with_house_number_dataset,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    fda_vendor_list_url = (
        "https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx"
    )
    page_size = 100
    vendor_category_code = "6"
    vendor_category_labels = {
        "0": "全部",
        "1": "食品公司",
        "2": "食品工廠",
        "3": "餐飲",
        "4": "通路",
        "6": "物流業",
    }
    city_aliases = {
        "臺北市": "台北市",
        "新北市": "新北市",
    }
    target_cities = ["臺北市", "新北市"]
    print(
        f"[{dag_id}] Start ETL: "
        f"cities={target_cities}, page_size={page_size}, category={vendor_category_code}"
    )

    def _extract_total_count(html):
        """從 FDA HTML 回應擷取總筆數。"""
        match = re.search(r"共\s*([0-9,]+)\s*筆", html)
        if not match:
            raise ValueError("Unable to find total record count in FDA response.")
        return int(match.group(1).replace(",", ""))

    def _split_registration_and_name(value):
        """拆分食品業者登錄字號與業者名稱。"""
        text = str(value).strip()
        match = re.match(r"^([A-Z]-\d{9}-\d{5}-\d)\s+(.+)$", text)
        if not match:
            return "", text
        return match.group(1), match.group(2).strip()

    def _normalize_address_for_geocoding(address):
        """清理地址字串，產生適合地理編碼的查詢地址。"""
        text = str(address).strip()
        text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        text = text.replace("台北市", "臺北市")
        text = re.sub(r"\s+", "", text)
        text = re.sub(r"^(新北市[^市縣]{2,3}區)新北市[^市縣]{2,3}區", r"\1", text)
        text = re.sub(r"^(臺北市[^市縣]{2,3}區)臺北市[^市縣]{2,3}區", r"\1", text)
        text = re.sub(r"[~～].*$", "", text)
        text = re.sub(r"([0-9一二三四五六七八九十]+)鄰", "", text)
        text = re.sub(r"(\d+)(?:樓|F|f)(?:之\d+)?(?:[至~-]\d+(?:樓|F|f))?$", "", text)
        text = re.sub(r"\d+樓.*$", "", text)
        return text

    def _create_session():
        """建立 FDA 查詢使用的 HTTP session。"""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        return session

    def _fetch_vendor_page(session, city, page):
        """向 FDA 縣市列表端點抓取指定城市與頁碼資料。"""
        print(
            f"[{dag_id}] Fetch FDA page: "
            f"city={city}, page={page}, size={page_size}"
        )
        response = session.get(
            fda_vendor_list_url,
            params={
                "req": "getlist",
                "city": city,
                "Page": page,
                "Size": page_size,
                "tp": vendor_category_code,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.text

    def _parse_vendor_page(html, city, page):
        """解析 FDA HTML 表格，轉成標準化業者欄位。"""
        tables = pd.read_html(StringIO(html))
        if not tables:
            return pd.DataFrame()

        data = tables[0].rename(
            columns={
                "登錄項目營業項目": "registration_item",
                "食品業者登錄字號名稱": "registration_and_name",
                "地址": "address",
                "公司/商業登記統一編號": "company_registration_name",
            }
        )
        data = data.drop(columns=["功能"], errors="ignore").dropna(how="all")
        if data.empty:
            print(
                f"[{dag_id}] Parsed FDA page is empty: "
                f"city={city}, page={page}"
            )
            return data

        split_values = data["registration_and_name"].apply(_split_registration_and_name)
        data["registration_no"] = split_values.apply(lambda item: item[0])
        data["name"] = split_values.apply(lambda item: item[1])
        data["city"] = city
        data["normalized_city"] = city_aliases.get(city, city)
        data["district"] = data["address"].apply(extract_district)
        data["vendor_category_code"] = vendor_category_code
        data["vendor_category"] = vendor_category_labels.get(vendor_category_code, "")
        data["source_page"] = page

        columns = [
            "city",
            "normalized_city",
            "district",
            "vendor_category_code",
            "vendor_category",
            "registration_item",
            "registration_no",
            "name",
            "address",
            "company_registration_name",
            "source_page",
        ]
        for column in columns:
            if column not in data.columns:
                data[column] = ""
        parsed = data[columns].fillna("")
        return parsed

    def _fetch_vendor_records(city):
        """抓取單一城市所有 FDA 物流業者頁面。"""
        print(f"[{dag_id}] Start fetching city: {city}")
        session = _create_session()
        first_html = _fetch_vendor_page(session, city, 1)
        total_count = _extract_total_count(first_html)
        total_pages = math.ceil(total_count / page_size)
        print(
            f"[{dag_id}] FDA city summary: "
            f"city={city}, total_count={total_count}, total_pages={total_pages}"
        )

        frames = [_parse_vendor_page(first_html, city, 1)]
        for page in range(2, total_pages + 1):
            html = _fetch_vendor_page(session, city, page)
            frames.append(_parse_vendor_page(html, city, page))

        data = pd.concat(frames, ignore_index=True)
        data.insert(0, "source_city_row_no", range(1, len(data) + 1))
        print(
            f"[{dag_id}] Finished fetching city: "
            f"city={city}, parsed_rows={len(data)}"
        )
        return total_count, data

    def _vendor_records_to_fallback_points(data):
        """將未定位成功的業者以行政區中心微偏移產生 fallback 點位。"""
        rows = []
        for (city, district), group in data.groupby(["city", "district"], dropna=False):
            if not district:
                continue
            centroid = DISTRICT_CENTROIDS.get(f"{city}{district}")
            if not centroid:
                continue

            total = len(group)
            radius = 0.004
            if total > 20:
                radius = 0.008
            if total > 50:
                radius = 0.012

            for idx, (_, row) in enumerate(group.reset_index(drop=True).iterrows()):
                key = f"{row.get('registration_no','')}|{row.get('address','')}|{idx}"
                digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
                angle = (int(digest[:8], 16) % 3600) / 10 * math.pi / 180
                ring = 0.35 + ((idx % 9) / 8) * 0.65
                lng = centroid[0] + math.cos(angle) * radius * ring
                lat = centroid[1] + math.sin(angle) * radius * ring
                rows.append(
                    {
                        "source_row_no": row["source_row_no"],
                        "fallback_lng": lng,
                        "fallback_lat": lat,
                    }
                )
        fallback = pd.DataFrame(
            rows, columns=["source_row_no", "fallback_lng", "fallback_lat"]
        )
        print(
            f"[{dag_id}] Built district fallback points: "
            f"rows={len(fallback)}"
        )
        return fallback

    def _geocode_with_tpgos(addresses):
        """使用 TPGOS 批次地址轉座標；缺少設定時略過。"""
        unique_addresses = pd.Series(addresses).dropna().astype(str).drop_duplicates()
        empty_result = pd.DataFrame(
            columns=["geocoding_address", "tpgos_lng", "tpgos_lat"]
        )
        if unique_addresses.empty:
            print(f"[{dag_id}] Skip TPGOS: no addresses")
            return empty_result

        try:
            from utils.transform_address import get_addr_xy_parallel

            print(
                f"[{dag_id}] Start TPGOS geocoding: "
                f"addresses={len(unique_addresses)}"
            )
            lng, lat = get_addr_xy_parallel(unique_addresses, sleep_time=0.5)
        except ImportError as error:
            print(f"[{dag_id}] Skip TPGOS geocoding import: {error}")
            return empty_result
        except Exception as error:
            print(f"[{dag_id}] Skip TPGOS geocoding: {error}")
            return empty_result

        result = pd.DataFrame(
            {
                "geocoding_address": unique_addresses,
                "tpgos_lng": lng,
                "tpgos_lat": lat,
            }
        )
        print(
            f"[{dag_id}] Finished TPGOS geocoding: "
            f"matched={result['tpgos_lng'].notna().sum()}, total={len(result)}"
        )
        return result

    def _geocode_records(records):
        """依縣市定位流程補上經緯度與定位方式。"""
        data = records.copy()
        print(
            f"[{dag_id}] Start geocoding records: "
            f"rows={len(data)}"
        )
        data["geocoding_address"] = data["address"].apply(_normalize_address_for_geocoding)
        data["taipei_house_key"] = ""
        data["taipei_house_lng"] = None
        data["taipei_house_lat"] = None
        data["taipei_house_location_method"] = ""

        taipei_mask = data["city"] == "臺北市"
        taipei_count = int(taipei_mask.sum())
        print(
            f"[{dag_id}] Start Taipei house-number geocoding: "
            f"addresses={data.loc[taipei_mask, 'geocoding_address'].dropna().nunique()}"
        )
        taipei_house_geocoded = geocode_taipei_addresses_with_house_number_dataset(
            data.loc[taipei_mask, "geocoding_address"]
        ).rename(columns={"address": "geocoding_address"})
        print(
            f"[{dag_id}] Finished Taipei house-number geocoding: "
            f"matched={taipei_house_geocoded['taipei_house_lng'].notna().sum()}, "
            f"taipei_rows={taipei_count}"
        )
        if not taipei_house_geocoded.empty:
            data = data.merge(
                taipei_house_geocoded,
                on="geocoding_address",
                how="left",
                suffixes=("", "_matched"),
            )
            for column in [
                "taipei_house_key",
                "taipei_house_lng",
                "taipei_house_lat",
                "taipei_house_location_method",
            ]:
                matched_column = f"{column}_matched"
                data[column] = data[matched_column].combine_first(data[column])
                data = data.drop(columns=[matched_column])

        tpgos_addresses = data.loc[
            ((data["city"] == "臺北市") & data["taipei_house_lng"].isna())
            | (data["city"] == "新北市"),
            "geocoding_address",
        ]
        print(
            f"[{dag_id}] TPGOS candidates: "
            f"addresses={pd.Series(tpgos_addresses).dropna().nunique()}"
        )
        data = data.merge(
            _geocode_with_tpgos(tpgos_addresses), on="geocoding_address", how="left"
        )

        missing_addresses = data.loc[
            data["taipei_house_lng"].isna() & data["tpgos_lng"].isna(),
            "geocoding_address",
        ]
        print(
            f"[{dag_id}] Start Nominatim geocoding: "
            f"addresses={pd.Series(missing_addresses).dropna().nunique()}"
        )
        osm_geocoded = geocode_addresses_with_osm(missing_addresses).rename(
            columns={"address": "geocoding_address"}
        )
        print(
            f"[{dag_id}] Finished Nominatim geocoding: "
            f"matched={osm_geocoded['osm_lng'].notna().sum()}, total={len(osm_geocoded)}"
        )
        data = data.merge(osm_geocoded, on="geocoding_address", how="left")

        fallback_points = _vendor_records_to_fallback_points(data)
        data = data.merge(fallback_points, on="source_row_no", how="left")
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
        data["location_method"] = "行政區中心微偏移"
        data.loc[
            data["osm_lng"].notna()
            & data["tpgos_lng"].isna()
            & data["taipei_house_lng"].isna(),
            "location_method",
        ] = data["osm_location_method"]
        data.loc[data["tpgos_lng"].notna(), "location_method"] = "地址轉座標"
        data.loc[data["taipei_house_lng"].notna(), "location_method"] = data[
            "taipei_house_location_method"
        ]

        osm_mask = (
            data["taipei_house_lng"].isna()
            & data["tpgos_lng"].isna()
            & data["osm_lng"].notna()
        )
        for index, row in data.loc[osm_mask].iterrows():
            data.loc[index, ["lng", "lat"]] = jitter_coordinate(
                row["lng"],
                row["lat"],
                f"{row.get('registration_no')}|{row.get('address')}|{row.get('source_row_no')}",
            )

        data["lng"] = data["lng"].fillna(data["fallback_lng"])
        data["lat"] = data["lat"].fillna(data["fallback_lat"])
        method_counts = data["location_method"].fillna("未定位").value_counts().to_dict()
        missing_count = int((data["lng"].isna() | data["lat"].isna()).sum())
        print(
            f"[{dag_id}] Finished geocoding records: "
            f"rows={len(data)}, missing={missing_count}, methods={method_counts}"
        )
        return data

    from_crs = 4326
    geometry_type = "Point"

    frames = []
    for city in target_cities:
        total_count, city_records = _fetch_vendor_records(city)
        if len(city_records) != total_count:
            print(
                f"[{dag_id}] FDA parsed row count differs from total: "
                f"city={city}, total_count={total_count}, parsed_rows={len(city_records)}"
            )
        frames.append(city_records)
    records = pd.concat(frames, ignore_index=True)
    records.insert(0, "source_row_no", range(1, len(records) + 1))
    print(
        f"[{dag_id}] Combined city records: "
        f"rows={len(records)}, by_city={records['city'].value_counts().to_dict()}"
    )

    data = _geocode_records(records)
    data["point_type"] = "業者點位"
    data = data.drop(
        columns=[
            "fallback_lng",
            "fallback_lat",
            "tpgos_lng",
            "tpgos_lat",
            "osm_lng",
            "osm_lat",
            "taipei_house_lng",
            "taipei_house_lat",
        ]
    )
    data["data_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime("%Y-%m-%d %H:%M:%S")
    lasttime_in_data = data["data_time"].max()

    if data.empty:
        raise ValueError("No Taipei/New Taipei FDA logistics vendor records found.")
    if data["lng"].isna().any() or data["lat"].isna().any():
        missing = data.loc[data["lng"].isna() | data["lat"].isna(), "address"].tolist()
        raise ValueError(f"Some FDA logistics vendor records were not geocoded: {missing}")

    print(f"[{dag_id}] Build WKB geometry")
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
            "source_city_row_no",
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
            "taipei_house_key",
            "lng",
            "lat",
            "wkb_geometry",
        ]
    ]

    print(
        f"[{dag_id}] Save ready data: "
        f"table={default_table}, rows={len(ready_data)}, load_behavior={load_behavior}"
    )
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
    print(
        f"[{dag_id}] Finished ETL: "
        f"dag_id={dag_id}, rows={len(ready_data)}, lasttime_in_data={lasttime_in_data}"
    )


dag = CommonDag(
    proj_folder="proj_city_dashboard",
    dag_folder="food_safety_logistics_vendor",
)
dag.create_dag(etl_func=_transfer)
