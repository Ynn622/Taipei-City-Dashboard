from airflow import DAG
from operators.common_pipeline import CommonDag

DATA_URL = "https://www.mohw.gov.tw/dl-17780-7b9267e9-feb4-4cf9-8cf2-1ecba76b22e8.html"
DATA_FILE_NAME = "food_processing_inspection.xlsx"

CATEGORY_MAP = {
    "肉品及其加工品": "肉品類",
    "蛋品及其加工品類": "蛋品類",
    "水產及其加工品類": "水產類",
    "鮮果蔬菜類及其加工品": "蔬果類",
    "食品添加物": "添加物",
}

TARGET_COUNTIES = {"臺北市", "新北市"}
TARGET_YEARS = set(range(105, 115))


def _food_processing_pass_rate(**kwargs):
    import re

    import pandas as pd
    from sqlalchemy import create_engine
    from utils.extract_stage import download_file
    from utils.load_stage import (
        save_dataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )

    def clean_text(val):
        if pd.isna(val):
            return ""
        s = str(val).strip()
        s = s.replace("\n", " ")
        s = re.sub(r"[\s\u3000]+", " ", s).strip()
        while True:
            new_s = re.sub(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])", r"\1\2", s)
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
                    minor = minor[len(current_major) :].strip()
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

    def parse_year_sheet(df):
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
                if pd.notna(v1) and isinstance(v1, (int, float)):
                    item["查驗件數"][col_name] = int(v1)
                if pd.notna(v2) and isinstance(v2, (int, float)):
                    item["不符規定件數"][col_name] = int(v2)

            records.append(item)
            i += 2

        return records

    def sum_category(item, category_prefix):
        inspection = 0
        non_compliant = 0
        for key, val in item["查驗件數"].items():
            if key.startswith(category_prefix + "_") and isinstance(val, (int, float)):
                inspection += int(val)
        for key, val in item["不符規定件數"].items():
            if key.startswith(category_prefix + "_") and isinstance(val, (int, float)):
                non_compliant += int(val)
        return inspection, non_compliant

    local_file = download_file(
        DATA_FILE_NAME,
        DATA_URL,
        is_proxy=False,
        is_verify=False,
    )

    xl = pd.ExcelFile(local_file)
    all_records = []

    for sheet_name in xl.sheet_names:
        if not sheet_name.endswith("年"):
            continue
        year_str = sheet_name.replace("年", "")
        try:
            year = int(year_str)
        except ValueError:
            continue
        if year not in TARGET_YEARS:
            continue

        df = pd.read_excel(local_file, sheet_name=sheet_name, header=None)
        items = parse_year_sheet(df)

        for item in items:
            county = item["縣市別"]
            if county not in TARGET_COUNTIES:
                continue
            for prefix, short_name in CATEGORY_MAP.items():
                inspection, non_compliant = sum_category(item, prefix)
                pass_rate = (
                    round((inspection - non_compliant) / inspection * 100, 2)
                    if inspection > 0
                    else 0
                )
                all_records.append(
                    {
                        "year": year,
                        "county": county,
                        "category": short_name,
                        "inspection_count": inspection,
                        "non_compliant_count": non_compliant,
                        "pass_rate": pass_rate,
                    }
                )

    ready_data = pd.DataFrame(all_records)
    ready_data = ready_data.sort_values(["year", "county", "category"]).reset_index(
        drop=True
    )

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    engine = create_engine(ready_data_db_uri)
    save_dataframe_to_postgresql(
        engine,
        data=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
    )
    update_lasttime_in_data_to_dataset_info(
        engine,
        dag_id,
        pd.Timestamp.now(),
    )


dag = CommonDag(
    proj_folder="proj_city_dashboard", dag_folder="food_processing_pass_rate"
)
dag.create_dag(etl_func=_food_processing_pass_rate)
