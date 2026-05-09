import re
import time

import pandas as pd
import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
DEFAULT_NOMINATIM_MIN_INTERVAL_SECONDS = 1.1
DEFAULT_NOMINATIM_USER_AGENT = "Taipei-City-Dashboard/1.0"
NOMINATIM_LOCATION_METHOD = "OpenStreetMap道路/地名定位"


def normalize_address_text(address):
    text = "" if pd.isna(address) else str(address).strip()
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    text = re.sub(r"\s+", "", text)
    return text


def default_query_candidates(address):
    text = normalize_address_text(address)
    if not text:
        return []

    candidates = [f"{text}, Taiwan"]
    city_variants = [text]
    if "台北市" in text:
        city_variants.append(text.replace("台北市", "臺北市"))
    if "臺北市" in text:
        city_variants.append(text.replace("臺北市", "台北市"))

    for variant in city_variants:
        if f"{variant}, Taiwan" not in candidates:
            candidates.append(f"{variant}, Taiwan")

        match = re.match(
            r"(?P<city>臺北市|台北市|新北市)(?P<district>[^市縣]{2,3}區)(?P<rest>.+)",
            variant,
        )
        if not match:
            continue

        city = match.group("city")
        district = match.group("district")
        rest = re.sub(r"^[^路街大道巷弄號]{2,4}里", "", match.group("rest"))
        road_match = re.match(
            r"(.+?(?:路|街|大道)(?:[一二三四五六七八九十0-9]+段)?)",
            rest,
        )
        if road_match:
            road = road_match.group(1)
            candidates.extend(
                [
                    f"{city}{district}{road}",
                    f"{road} {district} {city}",
                    f"{road}, {district}, {city}, Taiwan",
                ]
            )

    return list(dict.fromkeys(candidates))


def _normalize_queries(address, query_builder=None):
    if query_builder:
        queries = query_builder(address)
        if isinstance(queries, str):
            queries = [queries]
        return [str(query).strip() for query in queries if str(query).strip()]

    address = "" if pd.isna(address) else str(address).strip()
    return [f"{address}, Taiwan"] if address else []


def _empty_record(address, query=""):
    return {
        "address": address,
        "lng": None,
        "lat": None,
        "nominatim_query": query,
        "nominatim_display_name": "",
        "nominatim_location_method": "",
    }


def geocode_address_with_nominatim(
    address,
    session=None,
    last_request_time=None,
    min_interval_seconds=DEFAULT_NOMINATIM_MIN_INTERVAL_SECONDS,
    user_agent=DEFAULT_NOMINATIM_USER_AGENT,
    query_builder=None,
    countrycodes="tw",
    accept_language="zh-TW",
    timeout=30,
):
    queries = _normalize_queries(address, query_builder=query_builder)
    if not queries:
        return _empty_record(address)

    session = session or requests.Session()
    session.headers.update({"User-Agent": user_agent})
    last_request_time = last_request_time if last_request_time is not None else [0.0]

    record = _empty_record(address, queries[0])
    for query in queries:
        elapsed = time.monotonic() - last_request_time[0]
        if elapsed < min_interval_seconds:
            time.sleep(min_interval_seconds - elapsed)

        response = session.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": countrycodes,
                "accept-language": accept_language,
            },
            timeout=timeout,
        )
        last_request_time[0] = time.monotonic()
        response.raise_for_status()
        results = response.json()
        if not results:
            continue

        item = results[0]
        record = {
            "address": address,
            "lng": float(item["lon"]),
            "lat": float(item["lat"]),
            "nominatim_query": query,
            "nominatim_display_name": item.get("display_name", ""),
            "nominatim_location_method": NOMINATIM_LOCATION_METHOD,
        }
        break

    return record


def geocode_addresses_with_nominatim(
    addresses,
    min_interval_seconds=DEFAULT_NOMINATIM_MIN_INTERVAL_SECONDS,
    user_agent=DEFAULT_NOMINATIM_USER_AGENT,
    query_builder=None,
    countrycodes="tw",
    accept_language="zh-TW",
    timeout=30,
):
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    last_request_time = [0.0]

    rows = []
    for address in pd.Series(addresses).dropna().astype(str).drop_duplicates():
        rows.append(
            geocode_address_with_nominatim(
                address,
                session=session,
                last_request_time=last_request_time,
                min_interval_seconds=min_interval_seconds,
                user_agent=user_agent,
                query_builder=query_builder or default_query_candidates,
                countrycodes=countrycodes,
                accept_language=accept_language,
                timeout=timeout,
            )
        )

    return pd.DataFrame(
        rows,
        columns=[
            "address",
            "lng",
            "lat",
            "nominatim_query",
            "nominatim_display_name",
            "nominatim_location_method",
        ],
    )


def geocode_addresses_with_osm(
    addresses,
    delay_seconds=DEFAULT_NOMINATIM_MIN_INTERVAL_SECONDS,
    user_agent=DEFAULT_NOMINATIM_USER_AGENT,
    query_builder=None,
):
    data = geocode_addresses_with_nominatim(
        addresses,
        min_interval_seconds=delay_seconds,
        user_agent=user_agent,
        query_builder=query_builder,
    )
    return data.rename(
        columns={
            "lng": "osm_lng",
            "lat": "osm_lat",
            "nominatim_query": "osm_query",
            "nominatim_display_name": "osm_display_name",
            "nominatim_location_method": "osm_location_method",
        }
    )[
        [
            "address",
            "osm_lng",
            "osm_lat",
            "osm_query",
            "osm_display_name",
            "osm_location_method",
        ]
    ]
