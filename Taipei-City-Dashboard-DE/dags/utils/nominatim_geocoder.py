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
    text = text.replace("台北市", "臺北市")
    text = re.sub(r"^(新北市[^市縣]{2,3}區)新北市[^市縣]{2,3}區", r"\1", text)
    text = re.sub(r"^(臺北市[^市縣]{2,3}區)臺北市[^市縣]{2,3}區", r"\1", text)
    text = re.sub(r"[~～].*$", "", text)
    text = re.sub(r"([0-9一二三四五六七八九十]+)鄰", "", text)
    text = re.sub(r"(\d+)(?:樓|F|f)(?:之\d+)?(?:[至~-]\d+(?:樓|F|f))?$", "", text)
    text = re.sub(r"\d+樓.*$", "", text)
    if not text:
        return []

    candidates = [f"{text}, Taiwan"]
    match = re.match(
        r"(?P<city>臺北市|台北市|新北市)(?P<district>[^市縣]{2,3}區)(?P<rest>.+)",
        text,
    )
    if not match:
        return candidates

    city = match.group("city")
    district = match.group("district")
    rest = match.group("rest")
    rest_without_village = re.sub(r"^[^路街大道巷弄號]{2,4}里", "", rest)
    road_match = re.match(
        r"(.+?(?:路|街|大道)(?:[一二三四五六七八九十0-9]+段)?)",
        rest_without_village,
    )
    if not road_match:
        road_match = re.match(
            r"(.+?(?:路|街|大道)(?:[一二三四五六七八九十0-9]+段)?)", rest
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
        if "五股工業區" in rest:
            industrial_road_match = re.search(
                r"(五工(?:路|一路|二路|三路|四路|五路|六路))", rest
            )
            industrial_road = (
                industrial_road_match.group(1) if industrial_road_match else road
            )
            candidates.extend(
                [
                    f"{industrial_road} 五股區 {city}",
                    f"{city}五股區{industrial_road}",
                ]
            )
    else:
        place = re.split(r"[0-9一二三四五六七八九十]+(?:號|鄰|-|之)", rest)[0]
        place = re.sub(r"(里|村)$", "", place)
        if place:
            candidates.extend(
                [
                    f"{city}{district}{place}",
                    f"{place} {district} {city}",
                    f"{place}, {district}, {city}, Taiwan",
                ]
            )
        else:
            candidates.append(f"{city}{district}")

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
