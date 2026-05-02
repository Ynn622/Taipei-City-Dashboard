from operators.common_pipeline import CommonDag


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


def _cdc_infectious_disease(**kwargs):
    from datetime import date

    import pandas as pd
    from sqlalchemy import create_engine
    from utils.extract_stage import download_file
    from utils.load_stage import (
        save_dataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_time import convert_str_to_time_format

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

    def normalize_source(source):
        local_file = download_file(
            source["file_name"],
            source["url"],
            is_proxy=False,
            is_verify=False,
        )
        raw_data = pd.read_csv(local_file)
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

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    data = pd.concat([normalize_source(source) for source in SOURCES], ignore_index=True)

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
    weekly_data["diarrhea_visit_rate"] = (
        weekly_data["patient_visit"] / weekly_data["total_nhi_patient_visit"] * 100
    ).where(weekly_data["total_nhi_patient_visit"].notna())
    weekly_data["data_time"] = convert_str_to_time_format(weekly_data["data_time"])

    ready_data = weekly_data[
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
            "diarrhea_visit_rate",
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
        ready_data["data_time"].max(),
    )


dag = CommonDag(proj_folder="proj_city_dashboard", dag_folder="cdc_infectious_disease")
dag.create_dag(etl_func=_cdc_infectious_disease)
