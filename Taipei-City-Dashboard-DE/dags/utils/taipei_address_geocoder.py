import re
from pathlib import Path

import pandas as pd
import requests


TAIPEI_HOUSE_NUMBER_CSV_URL = (
    "https://data.taipei/api/frontstage/tpeod/dataset/resource.download"
    "?rid=ce76ca0c-7f94-4935-ab47-1d2a41ca2abb"
)
DEFAULT_TAIPEI_HOUSE_NUMBER_CACHE = "/tmp/taipei_house_number_positions.csv"
TAIPEI_HOUSE_NUMBER_LOCATION_METHOD = "臺北市門牌位置數值資料"

TAIPEI_DISTRICT_CODE_TO_NAME = {
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

CHINESE_SECTION_NUMBERS = {
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


def normalize_taipei_address_for_geocoding(address):
    text = "" if pd.isna(address) else str(address).strip()
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    text = text.replace("台北市", "臺北市")
    text = re.sub(r"\s+", "", text)
    if text and not text.startswith(("臺北市", "台北市")):
        text = f"臺北市{text}"
    text = re.sub(r"^(臺北市[^市縣]{2,3}區)臺北市[^市縣]{2,3}區", r"\1", text)
    text = re.sub(r"[~～].*$", "", text)
    text = re.sub(r"([0-9一二三四五六七八九十]+)鄰", "", text)
    text = re.sub(r"(\d+)(?:樓|F|f)(?:之\d+)?(?:[至~-]\d+(?:樓|F|f))?$", "", text)
    text = re.sub(r"\d+樓.*$", "", text)
    return text


def normalize_house_number_text(value):
    text = "" if pd.isna(value) else str(value).strip()
    if text.lower() in ("", "nan", "none"):
        return ""
    text = normalize_house_text(value)
    text = re.sub(r"(?:地下)?(?:[0-9]+|[一二三四五六七八九十]+)(?:樓|F|f).*", "", text)
    if text and re.search(r"\d", text) and not text.endswith(("號", "巷", "弄")):
        text += "號"
    return text


def normalize_house_text(value):
    text = "" if pd.isna(value) else str(value).strip()
    if text.lower() in ("", "nan", "none"):
        return ""
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    text = text.replace("－", "-").replace("—", "-")
    text = text.replace("-", "之")
    text = re.sub(r"[()（）]", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def normalize_road_text(value):
    text = normalize_house_text(value)
    for digit, chinese in sorted(
        CHINESE_SECTION_NUMBERS.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = text.replace(f"{digit}段", f"{chinese}段")
    return text


def extract_taipei_house_number_key(address):
    text = normalize_taipei_address_for_geocoding(address)
    match = re.match(
        r"(?:臺北市|台北市)(?P<district>[^市縣]{2,3}區)(?P<rest>.+)",
        text,
    )
    if not match:
        return None

    district = match.group("district")
    rest = match.group("rest")
    road_match = re.match(
        r"(?P<road>.+?(?:路|街|大道)(?:[一二三四五六七八九十0-9]+段)?)(?P<tail>.*)",
        rest,
    )
    if not road_match:
        return None

    road = normalize_road_text(road_match.group("road"))
    tail = normalize_house_number_text(road_match.group("tail"))
    lane_match = re.search(r"(?P<lane>\d+巷)", tail)
    alley_match = re.search(r"(?P<alley>\d+弄)", tail)
    number_match = re.search(r"(?P<number>\d+(?:之\d+)?號)", tail)
    if not number_match:
        return None

    return (
        district,
        road,
        lane_match.group("lane") if lane_match else "",
        alley_match.group("alley") if alley_match else "",
        number_match.group("number"),
    )


def download_taipei_house_number_csv(cache_path=DEFAULT_TAIPEI_HOUSE_NUMBER_CACHE):
    path = Path(cache_path)
    if path.exists() and path.stat().st_size > 0:
        return str(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(
        TAIPEI_HOUSE_NUMBER_CSV_URL,
        headers={"User-Agent": "TaipeiCityDashboardPrivate/taipei-address-geocoder"},
        timeout=300,
    )
    response.raise_for_status()
    path.write_bytes(response.content)
    return str(path)


def _empty_result(target_rows):
    return pd.DataFrame(
        [
            {
                **row,
                "taipei_house_lng": None,
                "taipei_house_lat": None,
                "taipei_house_location_method": "",
            }
            for row in target_rows
        ],
        columns=[
            "address",
            "taipei_house_key",
            "taipei_house_lng",
            "taipei_house_lat",
            "taipei_house_location_method",
        ],
    )


def geocode_taipei_addresses_with_house_number_dataset(
    addresses,
    csv_path=None,
    cache_path=DEFAULT_TAIPEI_HOUSE_NUMBER_CACHE,
    chunksize=100000,
):
    target_rows = []
    for address in pd.Series(addresses).dropna().astype(str).drop_duplicates():
        key = extract_taipei_house_number_key(address)
        target_rows.append({"address": address, "taipei_house_key": key})

    target_keys = {
        row["taipei_house_key"] for row in target_rows if row["taipei_house_key"]
    }
    if not target_keys:
        return _empty_result(target_rows)

    source_csv = csv_path or download_taipei_house_number_csv(cache_path)
    matched = {}
    usecols = ["鄉鎮市區代碼", "街路段", "巷", "弄", "號", "橫座標", "縱座標"]
    for chunk in pd.read_csv(
        source_csv, usecols=usecols, dtype=str, chunksize=chunksize
    ):
        chunk["district"] = chunk["鄉鎮市區代碼"].map(TAIPEI_DISTRICT_CODE_TO_NAME)
        chunk["key"] = list(
            zip(
                chunk["district"].fillna(""),
                chunk["街路段"].apply(normalize_road_text),
                chunk["巷"].fillna("").apply(normalize_house_number_text),
                chunk["弄"].fillna("").apply(normalize_house_number_text),
                chunk["號"].apply(normalize_house_number_text),
            )
        )
        hits = chunk[chunk["key"].isin(target_keys)]
        for _, row in hits.iterrows():
            key = row["key"]
            if key not in matched:
                matched[key] = (float(row["橫座標"]), float(row["縱座標"]))
        if len(matched) == len(target_keys):
            break

    transformer = None
    if matched:
        from pyproj import Transformer

        transformer = Transformer.from_crs("EPSG:3826", "EPSG:4326", always_xy=True)

    rows = []
    for row in target_rows:
        key = row["taipei_house_key"]
        if key in matched:
            lng, lat = transformer.transform(*matched[key])
            rows.append(
                {
                    **row,
                    "taipei_house_lng": lng,
                    "taipei_house_lat": lat,
                    "taipei_house_location_method": TAIPEI_HOUSE_NUMBER_LOCATION_METHOD,
                }
            )
        else:
            rows.append(
                {
                    **row,
                    "taipei_house_lng": None,
                    "taipei_house_lat": None,
                    "taipei_house_location_method": "",
                }
            )
    return pd.DataFrame(rows)


def geocode_taipei_addresses(
    addresses,
    csv_path=None,
    cache_path=DEFAULT_TAIPEI_HOUSE_NUMBER_CACHE,
    chunksize=100000,
):
    data = geocode_taipei_addresses_with_house_number_dataset(
        addresses,
        csv_path=csv_path,
        cache_path=cache_path,
        chunksize=chunksize,
    )
    return data.rename(
        columns={
            "taipei_house_lng": "lng",
            "taipei_house_lat": "lat",
            "taipei_house_location_method": "location_method",
        }
    )[["address", "lng", "lat", "location_method", "taipei_house_key"]]
