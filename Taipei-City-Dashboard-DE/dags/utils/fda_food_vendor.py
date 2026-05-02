import math
import re
import hashlib
import time
from pathlib import Path
from io import StringIO

import pandas as pd
import requests


FDA_VENDOR_LIST_URL = (
    "https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx"
)
TAIPEI_HOUSE_NUMBER_CSV_URL = (
    "https://data.taipei/api/frontstage/tpeod/dataset/resource.download"
    "?rid=ce76ca0c-7f94-4935-ab47-1d2a41ca2abb"
)
PAGE_SIZE = 40
TP_LOGISTICS = "6"
VENDOR_CATEGORY_LABELS = {
    "0": "全部",
    "1": "食品公司",
    "2": "食品工廠",
    "3": "餐飲",
    "4": "通路",
    "6": "物流業",
}
CITY_ALIASES = {
    "臺北市": "台北市",
    "新北市": "新北市",
}
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
DISTRICTS = [
    "中正區",
    "大同區",
    "中山區",
    "松山區",
    "大安區",
    "萬華區",
    "信義區",
    "士林區",
    "北投區",
    "內湖區",
    "南港區",
    "文山區",
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
DISTRICT_CENTROIDS = {
    "新北市三峽區": (121.413354, 24.893153),
    "新北市三芝區": (121.517466, 25.232291),
    "新北市三重區": (121.486201, 25.063365),
    "新北市中和區": (121.499489, 24.990292),
    "新北市五股區": (121.427650, 25.093573),
    "新北市八里區": (121.407976, 25.11546),
    "新北市土城區": (121.448033, 24.96548),
    "新北市坪林區": (121.732409, 24.923358),
    "新北市平溪區": (121.758048, 25.016928),
    "新北市新店區": (121.533978, 24.934005),
    "新北市新莊區": (121.428444, 25.032374),
    "新北市板橋區": (121.453898, 25.002968),
    "新北市林口區": (121.374907, 25.087785),
    "新北市樹林區": (121.402972, 24.98462),
    "新北市永和區": (121.517244, 25.004615),
    "新北市汐止區": (121.654072, 25.074906),
    "新北市泰山區": (121.407111, 25.059266),
    "新北市淡水區": (121.479584, 25.187318),
    "新北市深坑區": (121.622864, 24.995257),
    "新北市烏來區": (121.576788, 24.802641),
    "新北市瑞芳區": (121.830746, 25.098296),
    "新北市石碇區": (121.649352, 24.953388),
    "新北市石門區": (121.556422, 25.260311),
    "新北市萬里區": (121.650864, 25.180892),
    "新北市蘆洲區": (121.471517, 25.089373),
    "新北市貢寮區": (121.905344, 25.030129),
    "新北市金山區": (121.602872, 25.211978),
    "新北市雙溪區": (121.830835, 24.99552),
    "新北市鶯歌區": (121.34318, 24.958941),
    "臺北市中山區": (121.541478, 25.074745),
    "臺北市中正區": (121.521324, 25.024897),
    "臺北市信義區": (121.575052, 25.029492),
    "臺北市內湖區": (121.597575, 25.087621),
    "臺北市北投區": (121.523576, 25.159071),
    "臺北市南港區": (121.62122, 25.032316),
    "臺北市士林區": (121.547793, 25.130161),
    "臺北市大同區": (121.51117, 25.064),
    "臺北市大安區": (121.547859, 25.022626),
    "臺北市文山區": (121.572757, 24.986774),
    "臺北市松山區": (121.561326, 25.060093),
    "臺北市萬華區": (121.496474, 25.028308),
}


def extract_total_count(html):
    match = re.search(r"共\s*([0-9,]+)\s*筆", html)
    if not match:
        raise ValueError("Unable to find total record count in FDA response.")
    return int(match.group(1).replace(",", ""))


def split_registration_and_name(value):
    text = str(value).strip()
    match = re.match(r"^([A-Z]-\d{9}-\d{5}-\d)\s+(.+)$", text)
    if not match:
        return "", text
    return match.group(1), match.group(2).strip()


def extract_district(address):
    text = str(address).strip()
    text_without_city = re.sub(r"^(?:台北市|臺北市|新北市)", "", text)
    for district in DISTRICTS:
        if text_without_city.startswith(district):
            return district
    match = re.search(r"([一-龥]{2,3}區)", text)
    return match.group(1) if match else ""


def normalize_address_for_geocoding(address):
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


def normalize_house_number_text(value):
    text = str(value).strip()
    if text.lower() in ("", "nan", "none"):
        return ""
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    text = text.replace("－", "-").replace("—", "-")
    text = text.replace("-", "之")
    text = re.sub(r"[()（）]", "", text)
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"(?:地下)?(?:[0-9]+|[一二三四五六七八九十]+)(?:樓|F|f).*", "", text)
    if text and re.search(r"\d", text) and not text.endswith(("號", "巷", "弄")):
        text += "號"
    return text


def normalize_road_text(value):
    text = normalize_house_number_text(value)
    for digit, chinese in CHINESE_SECTION_NUMBERS.items():
        text = text.replace(f"{digit}段", f"{chinese}段")
    return text


def extract_taipei_house_number_key(address):
    text = normalize_address_for_geocoding(address)
    match = re.match(r"(?:臺北市|台北市)(?P<district>[^市縣]{2,3}區)(?P<rest>.+)", text)
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


def download_taipei_house_number_csv(
    cache_path="/tmp/taipei_house_number_positions.csv",
):
    path = Path(cache_path)
    if path.exists() and path.stat().st_size > 0:
        return str(path)

    response = requests.get(
        TAIPEI_HOUSE_NUMBER_CSV_URL,
        headers={"User-Agent": "TaipeiCityDashboardPrivate/food-safety-logistics"},
        timeout=300,
    )
    response.raise_for_status()
    path.write_bytes(response.content)
    return str(path)


def geocode_taipei_addresses_with_house_number_dataset(
    addresses, csv_path=None, cache_path="/tmp/taipei_house_number_positions.csv"
):
    target_rows = []
    for address in pd.Series(addresses).dropna().astype(str).drop_duplicates():
        key = extract_taipei_house_number_key(address)
        target_rows.append({"address": address, "taipei_house_key": key})

    target_keys = {
        row["taipei_house_key"] for row in target_rows if row["taipei_house_key"]
    }
    if not target_keys:
        return pd.DataFrame(
            [
                {
                    **row,
                    "taipei_house_lng": None,
                    "taipei_house_lat": None,
                    "taipei_house_location_method": "",
                }
                for row in target_rows
            ]
        )

    source_csv = csv_path or download_taipei_house_number_csv(cache_path)
    matched = {}
    usecols = ["鄉鎮市區代碼", "街路段", "巷", "弄", "號", "橫座標", "縱座標"]
    for chunk in pd.read_csv(source_csv, usecols=usecols, dtype=str, chunksize=100000):
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
                    "taipei_house_location_method": "臺北市門牌位置數值資料",
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


def extract_osm_query(address):
    return extract_osm_query_candidates(address)[0]


def extract_osm_query_candidates(address):
    text = normalize_address_for_geocoding(address)
    match = re.match(
        r"(?P<city>臺北市|台北市|新北市)(?P<district>[^市縣]{2,3}區)(?P<rest>.+)",
        text,
    )
    if not match:
        return [text]

    city = match.group("city")
    district = match.group("district")
    rest = match.group("rest")
    rest_without_village = re.sub(r"^[^路街大道巷弄號]{2,4}里", "", rest)
    candidates = []
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
                [f"{industrial_road} 五股區 {city}", f"{city}五股區{industrial_road}"]
            )
    else:
        place = re.split(r"[0-9一二三四五六七八九十]+(?:號|鄰|-|之)", rest)[0]
        place = re.sub(r"(里|村)$", "", place)
        if place:
            candidates.extend(
                [
                    f"{city}{district}{place}",
                    f"{place} {district} {city}",
                ]
            )
        else:
            candidates.append(f"{city}{district}")

    return list(dict.fromkeys(candidates))


def geocode_addresses_with_osm(addresses, delay_seconds=1.05):
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "TaipeiCityDashboardPrivate/food-safety-logistics "
                "(https://github.com/taipei-dashboard)"
            ),
        }
    )

    query_cache = {}
    rows = []
    for address in pd.Series(addresses).dropna().astype(str).drop_duplicates():
        queries = extract_osm_query_candidates(address)
        cache_key = tuple(queries)
        if cache_key not in query_cache:
            query_cache[cache_key] = {
                "osm_lng": None,
                "osm_lat": None,
                "osm_query": queries[0] if queries else "",
                "osm_display_name": "",
                "osm_location_method": "",
            }
            for query in queries:
                response = session.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": query,
                        "format": "jsonv2",
                        "limit": 1,
                        "countrycodes": "tw",
                        "accept-language": "zh-TW",
                    },
                    timeout=30,
                )
                response.raise_for_status()
                results = response.json()
                time.sleep(delay_seconds)
                if results:
                    item = results[0]
                    query_cache[cache_key] = {
                        "osm_lng": float(item["lon"]),
                        "osm_lat": float(item["lat"]),
                        "osm_query": query,
                        "osm_display_name": item.get("display_name", ""),
                        "osm_location_method": "OpenStreetMap道路/地名定位",
                    }
                    break

        rows.append({"address": address, **query_cache[cache_key]})

    columns = [
        "address",
        "osm_lng",
        "osm_lat",
        "osm_query",
        "osm_display_name",
        "osm_location_method",
    ]
    return pd.DataFrame(rows, columns=columns)


def jitter_coordinate(lng, lat, key, radius=0.00035):
    if pd.isna(lng) or pd.isna(lat):
        return lng, lat
    digest = hashlib.sha1(str(key).encode("utf-8")).hexdigest()
    angle = (int(digest[:8], 16) % 3600) / 10 * math.pi / 180
    ring = 0.35 + ((int(digest[8:10], 16) % 9) / 8) * 0.65
    return lng + math.cos(angle) * radius * ring, lat + math.sin(angle) * radius * ring


def create_session():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
        }
    )
    return session


def fetch_vendor_page(session, city, page, vendor_category_code=TP_LOGISTICS):
    response = session.get(
        FDA_VENDOR_LIST_URL,
        params={
            "req": "getlist",
            "city": city,
            "Page": page,
            "Size": PAGE_SIZE,
            "tp": vendor_category_code,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.text


def parse_vendor_page(html, city, page, vendor_category_code=TP_LOGISTICS):
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
        return data

    split_values = data["registration_and_name"].apply(split_registration_and_name)
    data["registration_no"] = split_values.apply(lambda item: item[0])
    data["name"] = split_values.apply(lambda item: item[1])
    data["city"] = city
    data["normalized_city"] = CITY_ALIASES.get(city, city)
    data["district"] = data["address"].apply(extract_district)
    data["vendor_category_code"] = vendor_category_code
    data["vendor_category"] = VENDOR_CATEGORY_LABELS.get(vendor_category_code, "")
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
    return data[columns].fillna("")


def fetch_vendor_records(city, vendor_category_code=TP_LOGISTICS):
    session = create_session()
    first_html = fetch_vendor_page(session, city, 1, vendor_category_code)
    total_count = extract_total_count(first_html)
    total_pages = math.ceil(total_count / PAGE_SIZE)

    frames = [parse_vendor_page(first_html, city, 1, vendor_category_code)]
    for page in range(2, total_pages + 1):
        html = fetch_vendor_page(session, city, page, vendor_category_code)
        frames.append(parse_vendor_page(html, city, page, vendor_category_code))

    data = pd.concat(frames, ignore_index=True)
    data.insert(0, "source_row_no", range(1, len(data) + 1))
    return total_count, data


def aggregate_vendor_by_district(data):
    rows = []
    for (city, normalized_city, district), group in data.groupby(
        ["city", "normalized_city", "district"], dropna=False
    ):
        if not district:
            continue
        centroid = DISTRICT_CENTROIDS.get(f"{city}{district}")
        if not centroid:
            continue
        samples = group["name"].dropna().astype(str).drop_duplicates().head(5).tolist()
        registrations = (
            group["registration_no"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .head(5)
            .tolist()
        )
        addresses = (
            group["address"].dropna().astype(str).drop_duplicates().head(3).tolist()
        )
        rows.append(
            {
                "city": city,
                "normalized_city": normalized_city,
                "district": district,
                "vendor_category_code": group["vendor_category_code"].iloc[0],
                "vendor_category": group["vendor_category"].iloc[0],
                "vendor_count": int(len(group)),
                "sample_vendors": "、".join(samples),
                "sample_registration_nos": "、".join(registrations),
                "address_examples": "、".join(addresses),
                "lng": centroid[0],
                "lat": centroid[1],
            }
        )
    return pd.DataFrame(rows).sort_values(["city", "district"]).reset_index(drop=True)


def vendor_records_to_points(data):
    records = data.copy()
    rows = []
    for (city, district), group in records.groupby(["city", "district"], dropna=False):
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
                    **row.to_dict(),
                    "point_type": "業者點位",
                    "location_method": "行政區中心微偏移",
                    "lng": lng,
                    "lat": lat,
                }
            )
    return (
        pd.DataFrame(rows).sort_values(["city", "source_row_no"]).reset_index(drop=True)
    )
