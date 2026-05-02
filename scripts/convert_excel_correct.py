import pandas as pd
import json
import re

INPUT_FILE = "10521-01-03食品衛生管理工作－按縣市別分1150331.xlsx"
OUTPUT_JSON = "10521-01-03食品衛生管理工作_correct.json"


def clean_text(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    s = s.replace("\n", " ")
    s = re.sub(r'[\s\u3000]+', ' ', s).strip()
    while True:
        new_s = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', s)
        if new_s == s:
            break
        s = new_s
    return s


def build_column_map(df, r1, r2):
    mapping = {}
    current_major = None
    for j in range(len(df.columns)):
        major = clean_text(df.iloc[r1, j])
        minor = clean_text(df.iloc[r2, j])

        if major:
            current_major = major

        if j == 0:
            mapping[j] = "縣市別"
        elif j == 2:
            mapping[j] = "_類型標記"
        elif j == 36:
            mapping[j] = "_右頁縣市別"
        elif minor:
            if current_major and minor.startswith(current_major):
                minor = minor[len(current_major):].strip()
            mapping[j] = f"{current_major}_{minor}" if current_major else minor
        elif major:
            mapping[j] = major
        else:
            mapping[j] = None
    return mapping


def find_data_start(df):
    for i in range(7, len(df)):
        val = clean_text(df.iloc[i, 0])
        if "總" in val:
            return i
    return 11


def parse_year_sheet(df, sheet_name):
    col_map = build_column_map(df, 5, 6)
    data_start = find_data_start(df)

    records = []
    i = data_start
    while i < len(df) - 1:
        row1 = df.iloc[i]
        row2 = df.iloc[i + 1]

        county = clean_text(row1.iloc[0])
        type1 = clean_text(row1.iloc[2])
        type2 = clean_text(row2.iloc[2])

        if not county or type1 != "查驗件數":
            i += 1
            continue
        if type2 != "不符規定件數":
            i += 1
            continue

        item = {"縣市別": county, "查驗件數": {}, "不符規定件數": {}}

        for col_idx, col_name in col_map.items():
            if col_name is None or col_name.startswith("_"):
                continue
            v1 = row1.iloc[col_idx]
            v2 = row2.iloc[col_idx]
            if pd.notna(v1):
                item["查驗件數"][col_name] = int(v1) if isinstance(v1, (int, float)) else v1
            if pd.notna(v2):
                item["不符規定件數"][col_name] = int(v2) if isinstance(v2, (int, float)) else v2

        records.append(item)
        i += 2

    return records


def parse_history_sheet(df):
    headers = []
    for j in range(2, len(df.columns)):
        h = clean_text(df.iloc[2, j])
        headers.append(h if h else f"col_{j}")

    records = []
    i = 3
    while i < len(df):
        year = clean_text(df.iloc[i, 0])
        type1 = clean_text(df.iloc[i, 1])

        if not year or type1 != "查驗件數":
            i += 1
            continue
        if i + 1 >= len(df):
            break

        type2 = clean_text(df.iloc[i + 1, 1])
        if type2 != "不符規定件數":
            i += 1
            continue

        item = {"年份": year, "查驗件數": {}, "不符規定件數": {}}
        for idx, col_idx in enumerate(range(2, len(df.columns))):
            h = headers[idx]
            v1 = df.iloc[i, col_idx]
            v2 = df.iloc[i + 1, col_idx]
            if pd.notna(v1):
                item["查驗件數"][h] = int(v1) if isinstance(v1, (int, float)) else v1
            if pd.notna(v2):
                item["不符規定件數"][h] = int(v2) if isinstance(v2, (int, float)) else v2

        records.append(item)
        i += 2

    return records


def parse_description_sheet(df):
    lines = []
    for i in range(len(df)):
        val = clean_text(df.iloc[i, 0])
        if val:
            lines.append(val)
    return lines


def main():
    xl = pd.ExcelFile(INPUT_FILE)
    result = {"file": INPUT_FILE, "sheets": {}}

    for sheet_name in xl.sheet_names:
        print(f"Processing: {sheet_name}")
        df = pd.read_excel(INPUT_FILE, sheet_name=sheet_name, header=None)

        if sheet_name == "編製說明":
            result["sheets"][sheet_name] = {
                "type": "description",
                "data": parse_description_sheet(df),
            }
        elif sheet_name == "歷年":
            data = parse_history_sheet(df)
            result["sheets"][sheet_name] = {
                "type": "historical_summary",
                "record_count": len(data),
                "data": data,
            }
            print(f"  -> {len(data)} year records")
        else:
            data = parse_year_sheet(df, sheet_name)
            result["sheets"][sheet_name] = {
                "type": "yearly_data",
                "year": sheet_name.replace("年", ""),
                "record_count": len(data),
                "data": data,
            }
            print(f"  -> {len(data)} county records")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Output: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
