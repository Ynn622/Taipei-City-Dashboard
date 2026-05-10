from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import json
    import re
    import time
    import xml.etree.ElementTree as ET
    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.district_geocoder import DISTRICT_CENTROIDS
    from utils.extract_stage import NewTaipeiAPIClient
    from utils.fda_food_vendor import (
        jitter_coordinate,
    )
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.nominatim_geocoder import geocode_addresses_with_osm
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    rid = "fc30f585-66d9-4233-a65e-c650d177ebfe"
    from_crs = 4326
    geometry_type = "Point"

    def _is_street_address(address):
        return bool(re.search(r"(路|街|巷|弄)", str(address)))

    def _normalize_land_text(value):
        return (
            str(value or "")
            .replace("臺", "台")
            .replace("蕃", "番")
            .replace("　", "")
            .replace(" ", "")
            .strip()
        )

    def _parse_land_address(address, district):
        normalized_address = _normalize_land_text(address)
        normalized_district = _normalize_land_text(district)
        land_match = re.search(
            r"([0-9０-９]{3,4})\s*-\s*([0-9０-９]{1,4})",
            normalized_address,
        )
        if land_match:
            main_no = land_match.group(1).translate(
                str.maketrans("０１２３４５６７８９", "0123456789")
            )
            sub_no = land_match.group(2).translate(
                str.maketrans("０１２３４５６７８９", "0123456789")
            )
            land_no = main_no.zfill(4) + sub_no.zfill(4)
        else:
            land_match = re.search(
                r"([0-9０-９]{3,4})\s*(?:地號|號)",
                normalized_address,
            )
            if not land_match:
                return None
            main_no = land_match.group(1).translate(
                str.maketrans("０１２３４５６７８９", "0123456789")
            )
            land_no = main_no.zfill(4) + "0000"

        section_name = normalized_address[: land_match.start()]
        section_name = re.sub(r"^新北市", "", section_name)
        if normalized_district and section_name.startswith(normalized_district):
            section_name = section_name[len(normalized_district) :]
        section_name = re.sub(r"(?:地號|等.*|土地).*$", "", section_name).strip()
        if not section_name or "段" not in section_name:
            return None
        return section_name, land_no

    def _load_xml(url):
        response = requests.get(url, timeout=20)
        if response.status_code != 200 or not response.content.strip():
            return None
        return ET.fromstring(response.content)

    def _load_town_codes():
        root = _load_xml("https://api.nlsc.gov.tw/other/ListTown/F")
        return {
            item.findtext("townname"): item.findtext("towncode")
            for item in root.findall(".//townItem")
        }

    def _load_land_sections(town_code):
        root = _load_xml(
            f"https://api.nlsc.gov.tw/other/ListLandSection/F/{town_code}"
        )
        if root is None:
            return []
        sections = []
        for item in root.findall(".//sectItem"):
            section_name = item.findtext("sectstr")
            sections.append(
                {
                    "office": item.findtext("office"),
                    "sect": item.findtext("sectcode"),
                    "name": section_name,
                    "key": _normalize_land_text(section_name),
                }
            )
        return sections

    def _match_land_section(section_name, sections):
        section_key = _normalize_land_text(section_name)
        exact_matches = [section for section in sections if section["key"] == section_key]
        if exact_matches:
            return exact_matches[0]
        fuzzy_matches = [
            section
            for section in sections
            if section_key in section["key"] or section["key"] in section_key
        ]
        if not fuzzy_matches:
            loose_section_key = section_key.replace("段", "")
            fuzzy_matches = [
                section
                for section in sections
                if loose_section_key in section["key"].replace("段", "")
                or section["key"].replace("段", "") in loose_section_key
            ]
        if fuzzy_matches:
            fuzzy_matches.sort(
                key=lambda section: abs(len(section["key"]) - len(section_key))
            )
            return fuzzy_matches[0]
        return None

    def _parse_jsonp(text):
        text = text.strip()
        if text.startswith("cb(") and text.endswith(")"):
            text = text[3:-1]
        return json.loads(text)

    def _query_cadastral_position(office, section_code, land_no):
        params = {
            "type": "2",
            "flag": "2",
            "office": office,
            "sect": section_code,
            "landno": land_no,
            "alpah": "0.5f",
            "imgflag": "1",
            "callback": "cb",
        }
        headers = {
            "Referer": "https://maps.nlsc.gov.tw/",
            "User-Agent": "TaipeiCityDashboardDemo/1.0",
        }
        last_response = None
        for attempt in range(8):
            response = requests.get(
                "https://landmaps.nlsc.gov.tw/S_Maps/qryTileMapIndex",
                params=params,
                headers=headers,
                timeout=30,
            )
            last_response = response.text
            if "請稍候" not in last_response:
                break
            time.sleep(0.8 + attempt * 0.25)

        payload = _parse_jsonp(last_response)
        if not payload or not isinstance(payload, list):
            return None

        rows = []
        for group in payload:
            if isinstance(group, list):
                rows.extend([item for item in group if isinstance(item, dict)])
            elif isinstance(group, dict):
                rows.append(group)

        xs = []
        ys = []
        for row in rows:
            for x_key, y_key in [("lx", "ly"), ("rx", "ry"), ("cx", "cy")]:
                if x_key not in row or y_key not in row:
                    continue
                try:
                    lng = float(row[x_key])
                    lat = float(row[y_key])
                except (TypeError, ValueError):
                    continue
                if 119 < lng < 123 and 21 < lat < 26:
                    xs.append(lng)
                    ys.append(lat)

        if not xs or not ys:
            return None
        return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

    def _geocode_cadastral_lands(data):
        town_codes = _load_town_codes()
        section_cache = {}
        position_cache = {}
        for index, row in data[data["lng"].isna() | data["lat"].isna()].iterrows():
            parsed_land = _parse_land_address(row["address"], row["district"])
            if not parsed_land:
                continue

            section_name, land_no = parsed_land
            town_code = town_codes.get(row["district"])
            if not town_code:
                continue

            if town_code not in section_cache:
                section_cache[town_code] = _load_land_sections(town_code)
            land_section = _match_land_section(
                section_name,
                section_cache[town_code],
            )
            if not land_section:
                continue

            cache_key = (land_section["office"], land_section["sect"], land_no)
            if cache_key not in position_cache:
                position_cache[cache_key] = _query_cadastral_position(*cache_key)
                time.sleep(0.15)
            position = position_cache[cache_key]
            if not position:
                continue

            lng, lat = position
            data.loc[index, "lng"] = lng
            data.loc[index, "lat"] = lat
            data.loc[index, "location_method"] = "地籍宗地圖形中心"
            data.loc[index, "geocoding_address"] = (
                f"新北市{row['district']}{land_section['name']}"
                f"{land_no[:4]}-{land_no[4:]}地號"
            )
        return data

    client = NewTaipeiAPIClient(rid, input_format="json")
    raw_data = pd.DataFrame(client.get_all_data(size=1000))
    raw_data = raw_data.dropna(how="all")
    raw_data = raw_data[raw_data["no"].notna()]

    data = raw_data.rename(
        columns={
            "no": "source_row_no",
            "operators": "operator",
            "counties": "city",
            "town": "district",
            "address": "address",
            "phone": "phone",
            "produce": "name",
            "date": "certification_valid_until",
            "farm": "area_ha",
            "test": "certification_status",
        }
    )

    for col in [
        "source_row_no",
        "operator",
        "city",
        "district",
        "address",
        "phone",
        "name",
        "certification_valid_until",
        "certification_status",
    ]:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["city"] = data["city"].replace({"新北市": "新北市"})
    data = data[data["city"] == "新北市"].copy()
    data["address"] = data["address"].where(
        data["address"].str.startswith("新北市"),
        "新北市" + data["district"] + data["address"],
    )
    data["area_ha"] = pd.to_numeric(data["area_ha"], errors="coerce")
    data["data_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    lasttime_in_data = data["data_time"].max()
    data["source_type"] = "有機農場"
    data["source_dataset"] = "新北市有機農場"
    data["source_url"] = (
        "https://data.ntpc.gov.tw/datasets/fc30f585-66d9-4233-a65e-c650d177ebfe"
    )
    data["geocoding_address"] = data["address"]

    street_addresses = data.loc[
        data["geocoding_address"].apply(_is_street_address),
        "geocoding_address",
    ]
    osm_geocoded = geocode_addresses_with_osm(street_addresses).rename(
        columns={"address": "geocoding_address"}
    )
    data = data.merge(osm_geocoded, on="geocoding_address", how="left")
    data["lng"] = data["osm_lng"]
    data["lat"] = data["osm_lat"]
    data["location_method"] = data["osm_location_method"]

    data = _geocode_cadastral_lands(data)

    missing = data["lng"].isna() | data["lat"].isna()
    for index, row in data.loc[missing].iterrows():
        centroid = DISTRICT_CENTROIDS.get(f"{row['city']}{row['district']}")
        if centroid:
            lng, lat = jitter_coordinate(centroid[0], centroid[1], row["source_row_no"])
            data.loc[index, "lng"] = lng
            data.loc[index, "lat"] = lat
            data.loc[index, "location_method"] = "行政區中心"

    if data["lng"].isna().any() or data["lat"].isna().any():
        raise ValueError("Some New Taipei food source records were not geocoded.")

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
            "phone",
            "certification_valid_until",
            "certification_status",
            "area_ha",
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
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="food_source_ntpe",
)
dag.create_dag(etl_func=_transfer)
