import argparse
from datetime import date
from pathlib import Path

import pandas as pd


SOURCES = [
    {
        "url": "https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv",
        "file_name": "NHI_Diarrhea.csv",
        "dataset_name": "健保門診及住院就診人次統計-腹瀉",
        "surveillance_type": "健保門診及住院",
        "disease_group": "腹瀉",
        "disease_name": "腹瀉",
        "patient_visit_col": "腹瀉健保就診人次",
        "total_visit_col": "健保就診總人次",
    },
    {
        "url": "https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv",
        "file_name": "RODS_AcuteDiarrhea.csv",
        "dataset_name": "急診傳染病監測統計-急性腹瀉",
        "surveillance_type": "急診傳染病監測",
        "disease_group": "腹瀉",
        "disease_name": "急性腹瀉",
        "visit_type": "急診",
        "patient_visit_col": "急性腹瀉急診就診人次",
    },
]

YEAR_FROM = 2016
YEAR_TO = 2026


def year_week_to_week_start(years, weeks):
    records = []
    for year, week in zip(years, weeks):
        year = int(year)
        week = int(week)
        max_week = date(year, 12, 28).isocalendar().week
        week = min(week, max_week)
        week_start = date.fromisocalendar(year, week, 1)
        records.append(
            {
                "year": week_start.isocalendar().year,
                "week": week_start.isocalendar().week,
                "data_time": week_start,
            }
        )
    return pd.DataFrame(records)


def normalize_county(value):
    if pd.isna(value):
        return value
    return str(value).strip().replace("台", "臺")


def read_source(source, input_dir):
    source_path = Path(input_dir, source["file_name"]) if input_dir else source["url"]
    raw_data = pd.read_csv(source_path)
    data = pd.DataFrame(
        {
            "year": raw_data["年"],
            "week": raw_data["週"],
            "age_group": raw_data["年齡別"],
            "county": raw_data["縣市"].apply(normalize_county),
            "county_code": raw_data["縣市別代碼"],
            "patient_visit": raw_data[source["patient_visit_col"]],
        }
    )
    data["visit_type"] = raw_data.get("就診類別", source.get("visit_type", ""))
    data["total_nhi_patient_visit"] = raw_data.get(
        source.get("total_visit_col", ""), pd.NA
    )
    data["dataset_name"] = source["dataset_name"]
    data["surveillance_type"] = source["surveillance_type"]
    data["disease_group"] = source["disease_group"]
    data["disease_name"] = source["disease_name"]
    week_data = year_week_to_week_start(data["year"], data["week"])
    data["source_year"] = data["year"]
    data["source_week"] = data["week"]
    data["year"] = week_data["year"]
    data["week"] = week_data["week"]
    data["data_time"] = week_data["data_time"]
    return data


def build_table(input_dir=None):
    data = pd.concat([read_source(source, input_dir) for source in SOURCES], ignore_index=True)
    int_cols = ["year", "week", "county_code", "patient_visit"]
    for col in int_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").astype("Int64")
    data["total_nhi_patient_visit"] = pd.to_numeric(
        data["total_nhi_patient_visit"], errors="coerce"
    ).astype("Int64")
    data = data[(data["year"] >= YEAR_FROM) & (data["year"] <= YEAR_TO)].copy()
    grouped_columns = [
        "data_time",
        "year",
        "week",
        "dataset_name",
        "surveillance_type",
        "disease_group",
        "disease_name",
        "visit_type",
        "age_group",
        "county",
        "county_code",
    ]
    weekly_data = (
        data.groupby(grouped_columns, dropna=False)
        .agg(
            patient_visit=("patient_visit", "sum"),
            total_nhi_patient_visit=(
                "total_nhi_patient_visit",
                lambda values: values.sum(min_count=1),
            ),
        )
        .reset_index()
    )
    weekly_data["patient_visit"] = weekly_data["patient_visit"].astype("Int64")
    weekly_data["total_nhi_patient_visit"] = weekly_data[
        "total_nhi_patient_visit"
    ].astype("Int64")
    return weekly_data[
        [
            "data_time",
            "year",
            "week",
            "dataset_name",
            "surveillance_type",
            "disease_group",
            "disease_name",
            "visit_type",
            "age_group",
            "county",
            "county_code",
            "patient_visit",
            "total_nhi_patient_visit",
        ]
    ].sort_values(
        [
            "year",
            "week",
            "dataset_name",
            "visit_type",
            "county",
            "age_group",
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=None)
    parser.add_argument(
        "--output",
        default="Taipei-City-Dashboard-DE/data/cdc_infectious_disease_combined.csv",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = build_table(args.input_dir)
    data.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"rows={len(data)}")
    print(f"columns={','.join(data.columns)}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
