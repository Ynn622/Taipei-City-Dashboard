import html
import re
from io import BytesIO
from urllib.parse import urljoin

import pandas as pd
import requests


TAIPEI_WATER_QUALITY_URL = (
    "https://tsis.dbas.gov.taipei/statis/webMain.aspx?"
    "sys=220&ymf=10600&kind=21&type=0&funid=a05021902&cycle=4&"
    "outmode=12&compmode=0&outkind=3&deflst=2&nzo=1"
)
TAIPEI_WATER_QUALITY_DATASET_URL = (
    "https://data.taipei/dataset/detail?id=9626c65d-8fe7-45bb-bbe2-7439bed81010"
)
NEW_TAIPEI_WATER_QUALITY_URL = "https://www.water.gov.tw/ch/WaterQuality?nodeId=4631"

TAIPEI_PLANT_LOCATIONS = {
    "直潭淨水場": (121.5310, 24.9520, "新店區"),
    "長興淨水場": (121.5460, 25.0150, "文山區"),
    "公館淨水場": (121.5320, 25.0140, "中正區"),
    "雙溪淨水場": (121.5720, 25.1010, "士林區"),
    "陽明淨水場": (121.5440, 25.1540, "北投區"),
}

NEW_TAIPEI_PLANT_LOCATIONS = {
    "貢寮淨水場": (121.9206, 25.0199),
    "老梅淨水場": (121.5497, 25.2921),
    "林莊淨水場": (121.6125, 25.2236),
    "坪林淨水場": (121.7118, 24.9365),
    "員山淨水場": (121.8076, 25.1055),
    "板新淨水場": (121.3766, 24.9389),
}

COMMON_COLUMNS = [
    "source_row_no",
    "name",
    "english_name",
    "city",
    "district",
    "address",
    "water_sources",
    "data_time",
    "qualified",
    "ph",
    "turbidity_ntu",
    "free_residual_chlorine_mg_l",
    "total_hardness_mg_l",
    "total_dissolved_solids_mg_l",
    "coliform_cfu_100ml",
    "source_dataset",
    "source_url",
    "location_method",
    "lng",
    "lat",
]


def _request(url, method="get", **kwargs):
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", "Mozilla/5.0")
    response = requests.request(
        method,
        url,
        headers=headers,
        timeout=kwargs.pop("timeout", 60),
        **kwargs,
    )
    response.raise_for_status()
    return response


def _to_float(value):
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)


def _clean_cell(value):
    text = re.sub(r"<[^>]+>", "", value)
    return html.unescape(text).strip()


def _extract_table_rows(page_html):
    rows = {}
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", page_html, flags=re.S | re.I):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.S | re.I)
        if len(cells) >= 3:
            rows[_clean_cell(cells[0])] = _clean_cell(cells[1])
    return rows


def fetch_taipei_water_quality():
    response = _request(TAIPEI_WATER_QUALITY_URL, timeout=120)
    raw = pd.read_csv(BytesIO(response.content), encoding="utf-8-sig")
    latest_period = raw["統計期"].max()
    latest = raw[raw["統計期"] == latest_period].copy()

    records = []
    for index, (plant_name, group) in enumerate(latest.groupby("淨水場別"), start=1):
        lng, lat, district = TAIPEI_PLANT_LOCATIONS[plant_name]
        records.append(
            {
                "source_row_no": index,
                "name": plant_name,
                "english_name": "",
                "city": "臺北市",
                "district": district,
                "address": "",
                "water_sources": "、".join(group["自來水水源別"].astype(str).unique()),
                "data_time": latest_period,
                "qualified": "年度均值",
                "ph": round(group["PH數值"].map(_to_float).mean(), 2),
                "turbidity_ntu": round(
                    group["濁度數值[散射濁度單位]"].map(_to_float).mean(), 2
                ),
                "free_residual_chlorine_mg_l": round(
                    group["自由有效餘氯數值[mg/L]"].map(_to_float).mean(), 2
                ),
                "total_hardness_mg_l": round(
                    group["總硬度數值[mg/L]"].map(_to_float).mean(), 1
                ),
                "total_dissolved_solids_mg_l": round(
                    group["總溶解固體量[mg/L]"].map(_to_float).mean(), 1
                ),
                "coliform_cfu_100ml": "、".join(
                    group["大腸桿菌群數[每百毫升菌落數]"].astype(str).unique()
                ),
                "source_dataset": "臺北自來水水質檢驗(淨水場清水水質)",
                "source_url": TAIPEI_WATER_QUALITY_DATASET_URL,
                "location_method": "固定淨水場座標",
                "lng": lng,
                "lat": lat,
            }
        )
    return pd.DataFrame(records, columns=COMMON_COLUMNS)


def fetch_new_taipei_water_quality():
    session = requests.Session()
    list_response = session.get(
        NEW_TAIPEI_WATER_QUALITY_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )
    list_response.raise_for_status()
    token_match = re.search(
        r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"',
        list_response.text,
    )
    if not token_match:
        raise ValueError("Unable to find water.gov.tw request verification token.")

    search_response = session.post(
        NEW_TAIPEI_WATER_QUALITY_URL,
        data={
            "__RequestVerificationToken": token_match.group(1),
            "SearchKeyword": "新北市",
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )
    search_response.raise_for_status()

    items = re.findall(
        r'<a class="perform_item" href="([^"]+)" title="([^"]+)">(.*?)</a>',
        search_response.text,
        flags=re.S | re.I,
    )
    records = []
    for index, (href, title, body) in enumerate(items, start=1):
        title = html.unescape(title).replace("—", "-")
        name_match = re.match(r"([^()]+)(?:\(([^)]+)\))?(新北市.+)", title)
        if not name_match:
            continue
        name = name_match.group(1).strip()
        english_name = (name_match.group(2) or "").strip()
        address = name_match.group(3).strip()
        district_match = re.search(r"新北市(.+?區)", address)
        district = district_match.group(1) if district_match else ""
        date_match = re.search(r"(20\d{2}/\d{2}/\d{2})", _clean_cell(body))
        detail_url = urljoin(NEW_TAIPEI_WATER_QUALITY_URL, href)
        detail_response = session.get(
            detail_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=60,
        )
        detail_response.raise_for_status()
        rows = _extract_table_rows(detail_response.text)
        lng, lat = NEW_TAIPEI_PLANT_LOCATIONS[name]

        records.append(
            {
                "source_row_no": index,
                "name": name,
                "english_name": english_name,
                "city": "新北市",
                "district": district,
                "address": address,
                "water_sources": "",
                "data_time": date_match.group(1) if date_match else "",
                "qualified": rows.get("水質合格否(Y/N)", ""),
                "ph": _to_float(rows.get("pH值(－)", "")),
                "turbidity_ntu": _to_float(rows.get("濁度(NTU)", "")),
                "free_residual_chlorine_mg_l": _to_float(
                    rows.get("自由有效餘氯(mg/L)", "")
                ),
                "total_hardness_mg_l": _to_float(rows.get("總硬度(mg/L)", "")),
                "total_dissolved_solids_mg_l": _to_float(
                    rows.get("總溶解固體量(mg/L)", "")
                ),
                "coliform_cfu_100ml": rows.get("大腸桿菌群(CFU/100mL)", ""),
                "source_dataset": "臺灣自來水公司平均水質",
                "source_url": detail_url,
                "location_method": "固定淨水場座標",
                "lng": lng,
                "lat": lat,
            }
        )
    return pd.DataFrame(records, columns=COMMON_COLUMNS)
