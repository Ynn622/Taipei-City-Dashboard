#!/usr/bin/env python3
import argparse
import json
import math
import os
import re
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests


NTPC_ZONES = [
    "萬里區",
    "金山區",
    "板橋區",
    "汐止區",
    "深坑區",
    "石碇區",
    "瑞芳區",
    "平溪區",
    "雙溪區",
    "貢寮區",
    "新店區",
    "坪林區",
    "烏來區",
    "永和區",
    "中和區",
    "土城區",
    "三峽區",
    "樹林區",
    "鶯歌區",
    "三重區",
    "新莊區",
    "泰山區",
    "林口區",
    "蘆洲區",
    "五股區",
    "八里區",
    "淡水區",
    "三芝區",
    "石門區",
]

NTPC_AWARD_URL = "https://foodtracer.health.ntpc.gov.tw/FoodMap/GetFoodAwardMarkers"
TPE_AWARD_URL = (
    "https://data.taipei/api/dataset/59579c19-a561-4564-8c0f-545bfb32c0f6/"
    "resource/c5646d80-9118-4439-b924-075f96371d75/download"
)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
TPE_HOUSE_NUMBER_URL = (
    "https://data.taipei/api/frontstage/tpeod/dataset/"
    "resource.download?rid=ce76ca0c-7f94-4935-ab47-1d2a41ca2abb"
)
DEFAULT_OUTPUT = (
    "Taipei-City-Dashboard-FE/public/mapData/fda_good_restaurants.geojson"
)
DEFAULT_CACHE = "scripts/.cache/fda_good_restaurants_nominatim_cache.json"
DEFAULT_TPE_HOUSE_NUMBER_CACHE = "scripts/.cache/tpe_house_numbers.csv"
NOMINATIM_MIN_INTERVAL_SECONDS = 1.1
NOMINATIM_USER_AGENT = "Taipei-City-Dashboard/1.0 (fda_good_restaurants_geojson)"
TPE_DISTRICT_PATTERN = (
    r"(中正區|大同區|中山區|松山區|大安區|萬華區|信義區|士林區|北投區|內湖區|南港區|文山區)"
)
TPE_DISTRICT_CODES = {
    "63000010": "松山區",
    "63000020": "信義區",
    "63000030": "大安區",
    "63000040": "中山區",
    "63000050": "中正區",
    "63000060": "大同區",
    "63000070": "萬華區",
    "63000080": "文山區",
    "63000090": "南港區",
    "63000100": "內湖區",
    "63000110": "士林區",
    "63000120": "北投區",
}
FULLWIDTH_TRANS = str.maketrans("０１２３４５６７８９", "0123456789")
SECTION_NUMBERS = {
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
    "10": "十",
}


def env_bool(name, default=True):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no"}


def normalize_address(address, city):
    address = "" if pd.isna(address) else str(address).strip()
    address = address.replace("台北市", "臺北市")
    address = re.sub(r"\s+", "", address)
    if city and address and not address.startswith(city):
        address = f"{city}{address}"
    address = re.sub(r"^(臺北市[^區]+區)臺北市[^區]+區", r"\1", address)
    address = re.sub(r"^(新北市[^區]+區)新北市[^區]+區", r"\1", address)
    return address


def normalize_house_text(value):
    value = "" if pd.isna(value) else str(value).strip()
    value = value.translate(FULLWIDTH_TRANS)
    value = value.replace("臺", "台")
    value = re.sub(r"\s+", "", value)
    return value


def normalize_road(value):
    value = normalize_house_text(value)
    for number, chinese_number in sorted(
        SECTION_NUMBERS.items(), key=lambda item: len(item[0]), reverse=True
    ):
        value = value.replace(f"{number}段", f"{chinese_number}段")
    return value


def normalize_number(value):
    value = normalize_house_text(value)
    match = re.search(r"\d+(?:之\d+)?號", value)
    return match.group(0) if match else value


def address_to_house_key(address):
    address = normalize_road(address)
    district_match = re.search(TPE_DISTRICT_PATTERN, address)
    if not district_match:
        return None

    district = district_match.group(1)
    rest = address[district_match.end() :]
    number_match = re.search(r"\d+(?:之\d+)?號", rest)
    if not number_match:
        return None

    number = number_match.group(0)
    before_number = rest[: number_match.start()]
    lane_match = re.search(r"(\d+巷)", before_number)
    alley_match = re.search(r"(\d+弄)", before_number)
    lane = lane_match.group(1) if lane_match else ""
    alley = alley_match.group(1) if alley_match else ""
    road_text = before_number
    if lane_match:
        road_text = road_text[: lane_match.start()]
    elif alley_match:
        road_text = road_text[: alley_match.start()]

    road_match = re.search(
        r"(.+?(?:大道|路|街)(?:[一二三四五六七八九十]+段)?)", road_text
    )
    road = road_match.group(1) if road_match else road_text
    road = normalize_road(road)
    if not road:
        return None

    return "|".join([district, road, lane, alley, number])


def twd97_to_wgs84(x, y):
    a = 6378137.0
    b = 6356752.314245
    lon0 = math.radians(121)
    k0 = 0.9999
    dx = 250000
    e = math.sqrt(1 - (b * b) / (a * a))

    x = float(x) - dx
    y = float(y)
    m = y / k0
    mu = m / (a * (1 - e**2 / 4 - 3 * e**4 / 64 - 5 * e**6 / 256))
    e1 = (1 - math.sqrt(1 - e**2)) / (1 + math.sqrt(1 - e**2))
    j1 = 3 * e1 / 2 - 27 * e1**3 / 32
    j2 = 21 * e1**2 / 16 - 55 * e1**4 / 32
    j3 = 151 * e1**3 / 96
    j4 = 1097 * e1**4 / 512
    fp = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu)
    fp += j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)

    e2 = e**2 / (1 - e**2)
    c1 = e2 * math.cos(fp) ** 2
    t1 = math.tan(fp) ** 2
    r1 = a * (1 - e**2) / (1 - e**2 * math.sin(fp) ** 2) ** 1.5
    n1 = a / math.sqrt(1 - e**2 * math.sin(fp) ** 2)
    d = x / (n1 * k0)

    lat = fp - (n1 * math.tan(fp) / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * e2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * e2 - 3 * c1**2)
        * d**6
        / 720
    )
    lon = lon0 + (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * e2 + 24 * t1**2)
        * d**5
        / 120
    ) / math.cos(fp)
    return math.degrees(lon), math.degrees(lat)


def parse_award(text):
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


def extract_ntpc_data(verify_ssl=True):
    response = requests.post(
        NTPC_AWARD_URL,
        data={"ZoneID": ",".join(NTPC_ZONES)},
        timeout=60,
        verify=verify_ssl,
    )
    response.raise_for_status()
    rows = []
    for item in response.json():
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


def load_cache(cache_path):
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache_path, cache):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def geocode_taipei_address(address, cache, cache_path, last_request_time):
    if not address:
        return address, None, None
    if address in cache:
        cached = cache[address]
        return address, cached.get("lng"), cached.get("lat")

    elapsed = time.monotonic() - last_request_time[0]
    if elapsed < NOMINATIM_MIN_INTERVAL_SECONDS:
        time.sleep(NOMINATIM_MIN_INTERVAL_SECONDS - elapsed)

    response = requests.get(
        NOMINATIM_URL,
        params={
            "format": "jsonv2",
            "limit": 1,
            "countrycodes": "tw",
            "accept-language": "zh-TW",
            "q": f"{address}, Taiwan",
        },
        headers={"User-Agent": NOMINATIM_USER_AGENT},
        timeout=30,
    )
    last_request_time[0] = time.monotonic()
    response.raise_for_status()
    results = response.json()
    if not results:
        cache[address] = {"lng": None, "lat": None}
        save_cache(cache_path, cache)
        return address, None, None
    first = results[0]
    lng = first.get("lon")
    lat = first.get("lat")
    cache[address] = {"lng": lng, "lat": lat}
    save_cache(cache_path, cache)
    return address, lng, lat


def geocode_addresses(addresses, cache, cache_path):
    last_request_time = [0.0]
    results = [
        geocode_taipei_address(address, cache, cache_path, last_request_time)
        for address in addresses
    ]
    return pd.DataFrame(results, columns=["address", "lng", "lat"])


def download_tpe_house_numbers(cache_path):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path

    response = requests.get(TPE_HOUSE_NUMBER_URL, stream=True, timeout=60)
    response.raise_for_status()
    with cache_path.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
    return cache_path


def load_tpe_house_number_lookup(cache_path):
    csv_path = download_tpe_house_numbers(cache_path)
    house_numbers = pd.read_csv(
        csv_path,
        usecols=["鄉鎮市區代碼", "街路段", "巷", "弄", "號", "橫座標", "縱座標"],
        dtype={
            "鄉鎮市區代碼": "string",
            "街路段": "string",
            "巷": "string",
            "弄": "string",
            "號": "string",
            "橫座標": "float64",
            "縱座標": "float64",
        },
    )
    house_numbers["district"] = house_numbers["鄉鎮市區代碼"].map(TPE_DISTRICT_CODES)
    house_numbers = house_numbers.dropna(
        subset=["district", "街路段", "號", "橫座標", "縱座標"]
    )
    house_numbers["road"] = house_numbers["街路段"].apply(normalize_road)
    house_numbers["lane"] = house_numbers["巷"].apply(normalize_house_text)
    house_numbers["alley"] = house_numbers["弄"].apply(normalize_house_text)
    house_numbers["number"] = house_numbers["號"].apply(normalize_number)
    house_numbers["house_key"] = house_numbers[
        ["district", "road", "lane", "alley", "number"]
    ].agg("|".join, axis=1)
    return house_numbers.drop_duplicates("house_key")[
        ["house_key", "橫座標", "縱座標"]
    ]


def geocode_with_tpe_house_numbers(addresses, house_number_cache_path):
    lookup = load_tpe_house_number_lookup(house_number_cache_path)
    data = pd.DataFrame({"address": addresses})
    data["house_key"] = data["address"].apply(address_to_house_key)
    data = pd.merge(data, lookup, on="house_key", how="left")
    coords = data.apply(
        lambda row: (
            twd97_to_wgs84(row["橫座標"], row["縱座標"])
            if pd.notna(row["橫座標"]) and pd.notna(row["縱座標"])
            else (None, None)
        ),
        axis=1,
        result_type="expand",
    )
    data["lng"] = coords[0]
    data["lat"] = coords[1]
    return data[["address", "lng", "lat"]]


def geocode_addresses_with_fallback(
    addresses, cache, cache_path, house_number_cache_path, skip_nominatim=False
):
    if skip_nominatim:
        coordinates = pd.DataFrame(
            {"address": addresses, "lng": None, "lat": None}
        )
    else:
        coordinates = geocode_addresses(addresses, cache, cache_path)

    missing = coordinates[coordinates["lng"].isna() | coordinates["lat"].isna()]
    if missing.empty:
        return coordinates

    fallback = geocode_with_tpe_house_numbers(
        pd.Series(missing["address"].unique()), house_number_cache_path
    )
    fallback = fallback.dropna(subset=["lng", "lat"])
    fallback = fallback.rename(columns={"lng": "fallback_lng", "lat": "fallback_lat"})
    coordinates = pd.merge(coordinates, fallback, on="address", how="left")
    coordinates["lng"] = coordinates["lng"].fillna(coordinates["fallback_lng"])
    coordinates["lat"] = coordinates["lat"].fillna(coordinates["fallback_lat"])
    return coordinates[["address", "lng", "lat"]]


def extract_tpe_data(
    award_year, cache, cache_path, house_number_cache_path, skip_nominatim=False
):
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

    coordinates = geocode_addresses_with_fallback(
        pd.Series(data["address"].unique()),
        cache,
        cache_path,
        house_number_cache_path,
        skip_nominatim=skip_nominatim,
    )
    data = pd.merge(data, coordinates, on="address", how="left")
    data["district"] = data["address"].str.extract(
        TPE_DISTRICT_PATTERN,
        expand=False,
    )
    data["award_year"] = award_year
    data["lng"] = pd.to_numeric(data["lng"], errors="coerce")
    data["lat"] = pd.to_numeric(data["lat"], errors="coerce")
    return data.dropna(subset=["lng", "lat"])


def to_feature_collection(data):
    features = []
    for row in data.to_dict("records"):
        lng = row.pop("lng")
        lat = row.pop("lat")
        features.append(
            {
                "type": "Feature",
                "properties": row,
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat],
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--cache", default=DEFAULT_CACHE)
    parser.add_argument("--house-number-cache", default=DEFAULT_TPE_HOUSE_NUMBER_CACHE)
    parser.add_argument(
        "--skip-nominatim",
        action="store_true",
        help="Use Taipei house-number open data directly for Taipei addresses.",
    )
    parser.add_argument(
        "--ntpc-no-verify",
        action="store_true",
        help="Disable SSL certificate verification only for the New Taipei API.",
    )
    args = parser.parse_args()

    cache_path = Path(args.cache)
    house_number_cache_path = Path(args.house_number_cache)
    cache = load_cache(cache_path)

    ntpc_verify_ssl = env_bool("FDA_GOOD_RESTAURANTS_NTPC_VERIFY_SSL", True)
    ntpc_data = extract_ntpc_data(verify_ssl=ntpc_verify_ssl and not args.ntpc_no_verify)
    if ntpc_data.empty:
        raise SystemExit("No New Taipei award data was extracted.")

    latest_year = int(ntpc_data["award_year"].max())
    tpe_data = extract_tpe_data(
        latest_year,
        cache,
        cache_path,
        house_number_cache_path,
        skip_nominatim=args.skip_nominatim,
    )
    data = pd.concat([ntpc_data, tpe_data], ignore_index=True)
    data = data[data["award_year"] == latest_year].copy()
    data = data[
        [
            "city",
            "district",
            "award_year",
            "restaurant_name",
            "address",
            "lng",
            "lat",
            "rating_result",
        ]
    ]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(to_feature_collection(data), ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(data)} features to {output}")


if __name__ == "__main__":
    main()
