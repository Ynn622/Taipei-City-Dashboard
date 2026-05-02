from io import BytesIO

import pandas as pd
import requests

from utils.fda_food_vendor import TAIPEI_DISTRICT_CODE_TO_NAME


TAIPEI_HEALTH_CENTER_URL = (
    "https://data.taipei/api/dataset/d4c6d4e0-c2b4-48e3-99b4-f670d820326b/"
    "resource/1e57f3cb-7063-4db7-a263-106ab9bdf6d1/download"
)
NEW_TAIPEI_HEALTH_OFFICE_URL = (
    "https://data.ntpc.gov.tw/api/datasets/"
    "2553bb1a-bcbb-4284-8b24-acfefe966f1e/csv/file"
)


def read_csv_from_url(url, encoding):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    response.raise_for_status()
    return pd.read_csv(BytesIO(response.content), encoding=encoding)


def complete_taipei_address(address, district):
    text = str(address).strip().replace("　", "")
    text = text.replace("台北巿", "臺北市").replace("臺北巿", "臺北市")
    text = text.replace("台北市", "臺北市")
    if text.startswith("臺北市"):
        without_city = text[len("臺北市") :]
        if without_city.startswith(district):
            return (
                f"臺北市{district}{without_city[len(district):].replace('臺北市', '')}"
            )
        return f"臺北市{district}{without_city}"
    return f"臺北市{district}{text}"


def fetch_taipei_health_centers():
    raw = read_csv_from_url(TAIPEI_HEALTH_CENTER_URL, encoding="cp950")
    data = raw.rename(
        columns={
            "健康服務中心名稱": "name",
            "行政區": "district_code",
            "地址": "address",
            "電話": "phone",
            "網址": "website",
        }
    )
    data["district_code"] = data["district_code"].astype(str)
    data["district"] = data["district_code"].map(TAIPEI_DISTRICT_CODE_TO_NAME)
    data["city"] = "臺北市"
    data["agency_type"] = "健康服務中心"
    data["address"] = data.apply(
        lambda row: complete_taipei_address(row["address"], row["district"]), axis=1
    )
    data["website"] = data["website"].astype(str).str.strip()
    data["source_dataset"] = "臺北市健康服務中心"
    data["source_url"] = "https://data.gov.tw/dataset/121146"
    data.insert(0, "source_row_no", range(1, len(data) + 1))
    result = data[
        [
            "source_row_no",
            "name",
            "city",
            "district",
            "district_code",
            "agency_type",
            "address",
            "phone",
            "website",
            "source_dataset",
            "source_url",
        ]
    ].fillna("")
    main_bureau = pd.DataFrame(
        [
            {
                "source_row_no": len(result) + 1,
                "name": "臺北市政府衛生局",
                "city": "臺北市",
                "district": "信義區",
                "district_code": "63000020",
                "agency_type": "衛生局",
                "address": "臺北市信義區市府路1號",
                "phone": "(02)27208889",
                "website": "https://health.gov.taipei/",
                "source_dataset": "臺北市政府衛生局",
                "source_url": "https://health.gov.taipei/",
            }
        ]
    )
    return pd.concat([result, main_bureau], ignore_index=True).fillna("")


def fetch_new_taipei_health_offices():
    raw = read_csv_from_url(NEW_TAIPEI_HEALTH_OFFICE_URL, encoding="utf-8-sig")
    data = raw.rename(
        columns={
            "seqno": "source_row_no",
            "hosp_id": "office_id",
            "hosp_name": "name",
            "tel": "phone",
            "hosp_addr": "address",
            "open time": "open_time",
        }
    )
    data["city"] = "新北市"
    data["agency_type"] = "衛生所"
    data["website"] = ""
    data["source_dataset"] = "新北市各區衛生所"
    data["source_url"] = "https://data.gov.tw/dataset/125693"
    result = data[
        [
            "source_row_no",
            "office_id",
            "name",
            "city",
            "district",
            "agency_type",
            "address",
            "phone",
            "extension",
            "zipcode",
            "open_time",
            "website",
            "source_dataset",
            "source_url",
        ]
    ].fillna("")
    main_bureau = pd.DataFrame(
        [
            {
                "source_row_no": len(result) + 1,
                "office_id": "",
                "name": "新北市政府衛生局",
                "city": "新北市",
                "district": "板橋區",
                "agency_type": "衛生局",
                "address": "新北市板橋區英士路192-1號",
                "phone": "(02)22577155",
                "extension": "",
                "zipcode": "220",
                "open_time": "",
                "website": "https://www.health.ntpc.gov.tw/",
                "source_dataset": "新北市政府衛生局",
                "source_url": "https://www.health.ntpc.gov.tw/",
            }
        ]
    )
    return pd.concat([result, main_bureau], ignore_index=True).fillna("")
