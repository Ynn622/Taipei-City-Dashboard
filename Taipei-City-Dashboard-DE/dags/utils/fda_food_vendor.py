import math
import re
import hashlib
from io import StringIO

import pandas as pd
import requests
from utils.district_geocoder import DISTRICT_CENTROIDS
from utils.taipei_address_geocoder import (
    TAIPEI_DISTRICT_CODE_TO_NAME,
    download_taipei_house_number_csv,
    extract_taipei_house_number_key,
    geocode_taipei_addresses_with_house_number_dataset,
    normalize_house_number_text,
    normalize_road_text,
)


FDA_VENDOR_LIST_URL = (
    "https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx"
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
