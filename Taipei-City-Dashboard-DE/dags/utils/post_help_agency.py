import re

import pandas as pd
import requests
from utils.fda_food_vendor import (
    DISTRICT_CENTROIDS,
    extract_district,
    geocode_addresses_with_osm,
    geocode_taipei_addresses_with_house_number_dataset,
    jitter_coordinate,
)


TAIPEI_MEDICAL_DATASETS = [
    {
        "page_id": "6fa3ed67-e60e-44d9-a366-ce7008e322de",
        "title": "臺北市藥局",
        "agency_type": "藥局",
        "specialty": "藥局",
    },
    {
        "page_id": "dfd0f10f-0f4d-4c92-96bc-997e7596297d",
        "title": "臺北市西醫一般科醫療機構",
        "agency_type": "西醫一般科",
        "specialty": "西醫一般科",
    },
    {
        "page_id": "dbb54bf8-74a8-475d-ae88-a0ec4262c39a",
        "title": "臺北市內科醫療機構",
        "agency_type": "內科",
        "specialty": "內科",
    },
    {
        "page_id": "34e855c7-7808-46d2-b9b1-f7244fe2b9b5",
        "title": "臺北市家庭醫學科醫療機構",
        "agency_type": "家庭醫學科",
        "specialty": "家庭醫學科",
    },
    {
        "page_id": "73452edf-a60f-4f47-86d0-d4295e4fa79d",
        "title": "臺北市急診醫學科醫療機構",
        "agency_type": "急診醫學科",
        "specialty": "急診醫學科",
    },
]

NEW_TAIPEI_MEDICAL_DATASETS = [
    {
        "rid": "f379e6dc-5a60-49a7-a47b-d3887566e157",
        "title": "新北市非健保特約藥局名單",
        "agency_type": "藥局",
        "specialty": "藥局",
        "is_nhi_contracted": "非健保特約",
    },
    {
        "rid": "fdbefc45-7005-49ab-a56d-41881e435dc2",
        "title": "新北市健保特約藥局名單",
        "agency_type": "藥局",
        "specialty": "藥局",
        "is_nhi_contracted": "健保特約",
    },
    {
        "rid": "ec49095f-7383-4008-ba4f-3208068ceaa8",
        "title": "新北市西醫一般科醫療機構",
        "agency_type": "西醫一般科",
        "specialty": "西醫一般科",
    },
    {
        "rid": "e8244d31-e0e5-459d-87ba-3c188706fbee",
        "title": "新北市內科醫療機構",
        "agency_type": "內科",
        "specialty": "內科",
    },
    {
        "rid": "9e1c1aba-4e0b-4d5a-8755-efa1f09abe65",
        "title": "新北市家庭醫學科醫療機構",
        "agency_type": "家庭醫學科",
        "specialty": "家庭醫學科",
    },
    {
        "rid": "7e4a9359-61dd-4a3c-9ebc-8e2b0b380a13",
        "title": "新北市急診學學科醫療機構",
        "agency_type": "急診醫學科",
        "specialty": "急診醫學科",
    },
]

PROTECTION_AGENCIES = [
    {
        "name": "消保會",
        "city": "臺北市",
        "district": "中正區",
        "address": "臺北市中正區北平東路2號",
        "phone": "",
        "agency_type": "消保會",
        "lng": 121.52031,
        "lat": 25.04522,
    },
    {
        "name": "臺北市消費者服務中心",
        "city": "臺北市",
        "district": "信義區",
        "address": "臺北市信義區市府路1號8樓",
        "phone": "",
        "agency_type": "消費者服務中心",
        "lng": 121.56451,
        "lat": 25.03752,
    },
    {
        "name": "新北市消費者服務中心",
        "city": "新北市",
        "district": "板橋區",
        "address": "新北市板橋區中山路1段161號1樓聯合服務中心",
        "phone": "",
        "agency_type": "消費者服務中心",
        "lng": 121.46577,
        "lat": 25.0120,
    },
    {
        "name": "消基會",
        "city": "臺北市",
        "district": "大安區",
        "address": "臺北市大安區復興南路1段390號10樓之3",
        "phone": "",
        "agency_type": "消基會",
        "lng": 121.54336,
        "lat": 25.03342,
    },
]


class NewTaipeiSimpleAPIClient:
    BASE_URL = "https://staging.data.ntpc.gov.tw/api/datasets"

    def __init__(self, rid, timeout=60):
        self.rid = rid
        self.timeout = timeout

    def get_data(self, **params):
        response = requests.get(
            f"{self.BASE_URL}/{self.rid}/json",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_all_data(self, size=1000):
        rows = []
        page = 0
        while True:
            data = self.get_data(page=page, size=size)
            if not data:
                break
            rows.extend(data)
            if len(data) < size:
                break
            page += 1
        return rows


def get_current_taipei_rid(page_id, timeout=30):
    response = requests.get(
        f"https://data.taipei/api/frontstage/tpeod/dataset.view?id={page_id}",
        timeout=timeout,
    )
    response.raise_for_status()
    resources = response.json().get("payload", {}).get("resources", [])
    if not resources:
        raise ValueError(f"No resources found for page_id={page_id}")
    return resources[0]["rid"]


def get_taipei_data(rid, timeout=60):
    response = requests.get(
        f"https://data.taipei/api/v1/dataset/{rid}",
        params={"scope": "resourceAquire", "limit": 1},
        timeout=timeout,
    )
    response.raise_for_status()
    count = response.json()["result"]["count"]
    rows = []
    for offset in range(0, count, 1000):
        response = requests.get(
            f"https://data.taipei/api/v1/dataset/{rid}",
            params={
                "scope": "resourceAquire",
                "offset": offset,
                "limit": 1000,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        rows.extend(response.json()["result"]["results"])
    return rows


def normalize_address(value):
    text = str(value or "").strip()
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    text = text.replace("台北市", "臺北市")
    text = re.sub(r"\s+", "", text)
    return text


def first_geocoding_address(value):
    text = normalize_address(value)
    return re.split(r"[；;]", text)[0]


def infer_taipei_district(address):
    district = extract_district(address)
    if district:
        return district
    road_to_district = {
        "鄭州路": "大同區",
        "常德街": "中正區",
    }
    for road, mapped_district in road_to_district.items():
        if road in str(address):
            return mapped_district
    return ""


def taipei_geocoding_address(address, district):
    text = first_geocoding_address(address)
    if re.match(r"^(臺北市|台北市)[^市縣]{2,3}區", text):
        return text
    if district:
        return re.sub(r"^(臺北市|台北市)", f"臺北市{district}", text)
    return text


def clean_text(value):
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def coalesce_unique(values):
    cleaned = []
    for value in values:
        text = clean_text(value)
        if text and text not in cleaned:
            cleaned.append(text)
    return "、".join(cleaned)


def protection_agency_dataframe(city):
    rows = []
    data_time = pd.Timestamp.now(tz="Asia/Taipei").strftime("%Y-%m-%d %H:%M:%S")
    for index, item in enumerate(PROTECTION_AGENCIES, start=1):
        if item["city"] != city:
            continue
        rows.append(
            {
                "data_time": data_time,
                "source_row_no": f"protection-{index}",
                "name": item["name"],
                "city": item["city"],
                "district": item["district"],
                "address": item["address"],
                "phone": item["phone"],
                "agency_group": "民間保護機構",
                "agency_type": item["agency_type"],
                "specialties": item["agency_type"],
                "specialty_count": 1,
                "service_types": item["agency_type"],
                "is_nhi_contracted": "",
                "source_dataset": item["agency_type"],
                "source_url": "",
                "geocoding_address": item["address"],
                "location_method": "固定地址座標",
                "lng": item["lng"],
                "lat": item["lat"],
            }
        )
    return pd.DataFrame(rows)


def fetch_taipei_medical_records():
    rows = []
    for dataset in TAIPEI_MEDICAL_DATASETS:
        rid = get_current_taipei_rid(dataset["page_id"])
        raw_data = pd.DataFrame(get_taipei_data(rid))
        if raw_data.empty:
            continue
        raw_data = raw_data.dropna(how="all")
        for _, row in raw_data.iterrows():
            name = clean_text(row.get("機構名稱"))
            address = clean_text(row.get("地址"))
            if not name or not address:
                continue
            phone = coalesce_unique([row.get("電話"), row.get("其他電話")])
            data_time = row.get("_importdate", {})
            district = infer_taipei_district(address)
            rows.append(
                {
                    "data_time": data_time.get("date")
                    if isinstance(data_time, dict)
                    else "",
                    "source_row_no": clean_text(row.get("序號") or row.get("_id")),
                    "name": name,
                    "city": "臺北市",
                    "district": district,
                    "address": normalize_address(address),
                    "phone": phone,
                    "agency_group": "醫療機構",
                    "agency_type": dataset["agency_type"],
                    "specialty": dataset["specialty"],
                    "service_type": dataset["agency_type"],
                    "is_nhi_contracted": "",
                    "source_dataset": dataset["title"],
                    "source_url": (
                        "https://data.taipei/dataset/detail?id="
                        f"{dataset['page_id']}"
                    ),
                    "geocoding_address": taipei_geocoding_address(address, district),
                    "location_method": "來源座標",
                    "lng": pd.to_numeric(row.get("x"), errors="coerce"),
                    "lat": pd.to_numeric(row.get("y"), errors="coerce"),
                }
            )
    return pd.DataFrame(rows)


def fetch_new_taipei_medical_records():
    rows = []
    data_time = pd.Timestamp.now(tz="Asia/Taipei").strftime("%Y-%m-%d %H:%M:%S")
    for dataset in NEW_TAIPEI_MEDICAL_DATASETS:
        client = NewTaipeiSimpleAPIClient(dataset["rid"])
        raw_data = pd.DataFrame(client.get_all_data(size=1000))
        if raw_data.empty:
            continue
        raw_data = raw_data.dropna(how="all")
        for _, row in raw_data.iterrows():
            name = clean_text(row.get("name"))
            address = clean_text(row.get("address"))
            if not name or not address:
                continue
            district = clean_text(row.get("district")) or extract_district(address)
            rows.append(
                {
                    "data_time": data_time,
                    "source_row_no": clean_text(row.get("no")),
                    "name": name,
                    "city": "新北市",
                    "district": district,
                    "address": normalize_address(address),
                    "phone": clean_text(row.get("telephone")),
                    "agency_group": "醫療機構",
                    "agency_type": dataset["agency_type"],
                    "specialty": clean_text(row.get("division"))
                    or dataset["specialty"],
                    "service_type": dataset["agency_type"],
                    "is_nhi_contracted": dataset.get("is_nhi_contracted", ""),
                    "source_dataset": dataset["title"],
                    "source_url": (
                        "https://staging.data.ntpc.gov.tw/datasets/"
                        f"{dataset['rid']}"
                    ),
                    "geocoding_address": first_geocoding_address(address),
                    "location_method": "來源座標",
                    "lng": pd.to_numeric(row.get("wgs84ax"), errors="coerce"),
                    "lat": pd.to_numeric(row.get("wgs84ay"), errors="coerce"),
                }
            )
    return pd.DataFrame(rows)


def geocode_taipei_missing(data):
    missing = data["lng"].isna() | data["lat"].isna()
    if not missing.any():
        return data

    targets = data.loc[missing, "geocoding_address"]
    house_geocoded = geocode_taipei_addresses_with_house_number_dataset(
        targets
    ).rename(columns={"address": "geocoding_address"})
    data = data.merge(house_geocoded, on="geocoding_address", how="left")
    data["lng"] = data["lng"].combine_first(data["taipei_house_lng"])
    data["lat"] = data["lat"].combine_first(data["taipei_house_lat"])
    data["location_method"] = data["location_method"].where(
        data["taipei_house_lng"].isna(),
        data["taipei_house_location_method"],
    )
    data = data.drop(
        columns=[
            "taipei_house_key",
            "taipei_house_lng",
            "taipei_house_lat",
            "taipei_house_location_method",
        ],
        errors="ignore",
    )
    return data


def geocode_with_osm_for_missing(data):
    missing = data["lng"].isna() | data["lat"].isna()
    if not missing.any():
        return data
    osm_geocoded = geocode_addresses_with_osm(
        data.loc[missing, "geocoding_address"]
    ).rename(columns={"address": "geocoding_address"})
    data = data.merge(osm_geocoded, on="geocoding_address", how="left")
    data["lng"] = data["lng"].combine_first(data["osm_lng"])
    data["lat"] = data["lat"].combine_first(data["osm_lat"])
    data["location_method"] = data["location_method"].where(
        data["osm_lng"].isna(),
        data["osm_location_method"],
    )
    return data.drop(
        columns=["osm_lng", "osm_lat", "osm_query", "osm_display_name", "osm_location_method"],
        errors="ignore",
    )


def fill_missing_with_centroids(data):
    missing = data["lng"].isna() | data["lat"].isna()
    for index, row in data.loc[missing].iterrows():
        centroid = DISTRICT_CENTROIDS.get(f"{row['city']}{row['district']}")
        if centroid:
            lng, lat = jitter_coordinate(centroid[0], centroid[1], row["name"])
            data.loc[index, "lng"] = lng
            data.loc[index, "lat"] = lat
            data.loc[index, "location_method"] = "行政區中心"
    return data


def aggregate_agencies(data):
    data = data.copy()
    data["dedupe_key"] = (
        data["city"].fillna("")
        + "|"
        + data["name"].fillna("").str.replace(r"\s+", "", regex=True)
        + "|"
        + data["address"].fillna("").apply(normalize_address)
    )
    grouped = []
    for _, group in data.groupby("dedupe_key", sort=False):
        first = group.iloc[0]
        specialties = coalesce_unique(group.get("specialty", group["agency_type"]))
        service_types = coalesce_unique(group["service_type"])
        agency_types = coalesce_unique(group["agency_type"])
        grouped.append(
            {
                "data_time": coalesce_unique(group["data_time"]),
                "source_row_no": coalesce_unique(group["source_row_no"]),
                "name": first["name"],
                "city": first["city"],
                "district": first["district"],
                "address": first["address"],
                "phone": coalesce_unique(group["phone"]),
                "agency_group": first["agency_group"],
                "agency_type": agency_types,
                "specialties": specialties,
                "specialty_count": len([item for item in specialties.split("、") if item]),
                "service_types": service_types,
                "is_nhi_contracted": coalesce_unique(group["is_nhi_contracted"]),
                "source_dataset": coalesce_unique(group["source_dataset"]),
                "source_url": coalesce_unique(group["source_url"]),
                "geocoding_address": first["geocoding_address"],
                "location_method": first["location_method"],
                "lng": first["lng"],
                "lat": first["lat"],
            }
        )
    return pd.DataFrame(grouped)


def build_post_help_agency(city):
    if city == "臺北市":
        data = fetch_taipei_medical_records()
        data = geocode_taipei_missing(data)
    elif city == "新北市":
        data = fetch_new_taipei_medical_records()
    else:
        raise ValueError("city must be '臺北市' or '新北市'.")

    data = fill_missing_with_centroids(data)
    protection = protection_agency_dataframe(city)
    data = pd.concat([data, protection], ignore_index=True)
    data = aggregate_agencies(data)

    if data["lng"].isna().any() or data["lat"].isna().any():
        missing = data.loc[data["lng"].isna() | data["lat"].isna(), ["name", "address"]]
        raise ValueError(f"Some post-help agencies were not geocoded: {missing}")

    return data[
        [
            "data_time",
            "source_row_no",
            "name",
            "city",
            "district",
            "address",
            "phone",
            "agency_group",
            "agency_type",
            "specialties",
            "specialty_count",
            "service_types",
            "is_nhi_contracted",
            "source_dataset",
            "source_url",
            "geocoding_address",
            "location_method",
            "lng",
            "lat",
        ]
    ]
