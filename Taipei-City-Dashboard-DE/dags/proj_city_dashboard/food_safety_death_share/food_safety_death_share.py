from airflow import DAG
from operators.common_pipeline import CommonDag

TAIPEI_URL = (
    "https://tsis.dbas.gov.taipei/statis/webMain.aspx?sys=220&ymf=8100&kind=21"
    "&type=0&funid=A05032801&cycle=4&outmode=12&compmode=0&outkind=1"
    "&deflst=2&nzo=1"
)
NEW_TAIPEI_RID = "e490f906-93f0-4fc3-b5b3-fe34fb31d1db"
CAUSES = [
    "心臟疾病",
    "糖尿病",
    "腎炎腎徵候群及腎性病變",
    "慢性肝病及肝硬化",
]


def _transfer(**kwargs):
    import re
    from io import StringIO

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text as sa_text
    from utils.get_time import get_tpe_now_time_str
    from utils.load_stage import (
        save_dataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")
    data_time = get_tpe_now_time_str(is_with_tz=True)
    request_headers = {"User-Agent": "Mozilla/5.0"}

    def _normalize_text(value):
        return re.sub(r"\s+", "", str(value or "")).strip()

    def _normalize_columns(data):
        data = data.copy()
        data.columns = [str(col).strip() for col in data.columns]
        return data

    def _find_column(data, candidates):
        normalized_map = {_normalize_text(col): col for col in data.columns}
        for candidate in candidates:
            key = _normalize_text(candidate)
            if key in normalized_map:
                return normalized_map[key]
        for candidate in candidates:
            key = _normalize_text(candidate)
            for normalized_col, original_col in normalized_map.items():
                if key in normalized_col:
                    return original_col
        raise KeyError(f"Cannot find any column matching {candidates}")

    def _to_number(value):
        if pd.isna(value):
            return pd.NA
        text = str(value).strip().replace(",", "")
        if text in {"", "-", "...", "X", "x"}:
            return pd.NA
        return pd.to_numeric(text, errors="coerce")

    def _to_year(value):
        text = str(value).strip()
        match = re.search(r"\d+", text)
        if not match:
            return pd.NA
        year = int(match.group())
        return year + 1911 if year < 1911 else year

    def _latest_10_years(data):
        frames = []
        for city, city_data in data.groupby("city"):
            years = sorted(city_data["year"].dropna().unique(), reverse=True)[:10]
            frames.append(city_data[city_data["year"].isin(years)])
        return pd.concat(frames, ignore_index=True) if frames else data

    def _load_taipei():
        response = requests.get(TAIPEI_URL, headers=request_headers, timeout=60)
        response.raise_for_status()
        raw_data = pd.read_csv(StringIO(response.content.decode("utf-8-sig")))
        raw_data = _normalize_columns(raw_data).dropna(how="all")

        year_col = _find_column(raw_data, ["統計期", "年度", "年"])
        all_cause_col = _find_column(
            raw_data,
            ["死亡率/ 所有死亡原因", "死亡率/所有死亡原因"],
        )
        cause_columns = {
            cause: _find_column(raw_data, [f"死亡率/ {cause}", f"死亡率/{cause}"])
            for cause in CAUSES
        }

        rows = []
        for _, row in raw_data.iterrows():
            year = _to_year(row[year_col])
            all_cause_value = _to_number(row[all_cause_col])
            if pd.isna(year) or pd.isna(all_cause_value) or all_cause_value == 0:
                continue
            for cause, cause_col in cause_columns.items():
                cause_value = _to_number(row[cause_col])
                if pd.isna(cause_value):
                    continue
                rows.append(
                    {
                        "data_time": data_time,
                        "year": int(year),
                        "city": "臺北市",
                        "death_cause": cause,
                        "metric_basis": "死亡率",
                        "cause_value": float(cause_value),
                        "all_cause_value": float(all_cause_value),
                        "death_share_percent": round(
                            float(cause_value) / float(all_cause_value) * 100,
                            2,
                        ),
                    }
                )
        return pd.DataFrame(rows)

    def _new_taipei_col(row, number):
        candidates = [
            f"itemvalue{number}",
            f"item value{number}",
            f"item_value{number}",
        ]
        for candidate in candidates:
            if candidate in row:
                return row[candidate]
        normalized = {_normalize_text(key): key for key in row.keys()}
        for candidate in candidates:
            key = _normalize_text(candidate)
            if key in normalized:
                return row[normalized[key]]
        return pd.NA

    def _load_new_taipei():
        frames = []
        page = 0
        page_size = 100
        url = f"https://data.ntpc.gov.tw/api/datasets/{NEW_TAIPEI_RID}/csv"
        while True:
            response = requests.get(
                url,
                params={"page": page, "size": page_size},
                headers=request_headers,
                timeout=60,
            )
            response.raise_for_status()
            response_text = response.content.decode("utf-8-sig")
            if not response_text.strip():
                break

            page_data = pd.read_csv(StringIO(response_text))
            if page_data.empty:
                break

            frames.append(page_data)
            if len(page_data) < page_size:
                break
            page += 1

        raw_data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        raw_data = _normalize_columns(raw_data).dropna(how="all")

        cause_map = {
            "心臟疾病": (6, 7),
            "糖尿病": (10, 11),
            "腎炎腎徵候群及腎性病變": (14, 15),
            "慢性肝病及肝硬化": (20, 21),
        }
        rows = []
        for _, row in raw_data.iterrows():
            year = _to_year(row.get("field1"))
            all_cause_value = _to_number(_new_taipei_col(row, 2))
            all_cause_value = all_cause_value + _to_number(_new_taipei_col(row, 3))
            if pd.isna(year) or pd.isna(all_cause_value) or all_cause_value == 0:
                continue
            for cause, (male_col, female_col) in cause_map.items():
                cause_value = _to_number(_new_taipei_col(row, male_col))
                cause_value = cause_value + _to_number(_new_taipei_col(row, female_col))
                if pd.isna(cause_value):
                    continue
                rows.append(
                    {
                        "data_time": data_time,
                        "year": int(year),
                        "city": "新北市",
                        "death_cause": cause,
                        "metric_basis": "死亡人數",
                        "cause_value": float(cause_value),
                        "all_cause_value": float(all_cause_value),
                        "death_share_percent": round(
                            float(cause_value) / float(all_cause_value) * 100,
                            2,
                        ),
                    }
                )
        return pd.DataFrame(rows)

    def _ensure_ready_table(engine):
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS public.{default_table} (
                data_time timestamp with time zone,
                year integer,
                city text,
                death_cause text,
                metric_basis text,
                cause_value double precision,
                all_cause_value double precision,
                death_share_percent double precision
            )
        """
        create_index_sql = f"""
            CREATE INDEX IF NOT EXISTS {default_table}_city_year_idx
                ON public.{default_table} (city, year, death_cause)
        """
        with engine.begin() as conn:
            conn.execute(sa_text(create_table_sql))
            conn.execute(sa_text(create_index_sql))

    ready_data = pd.concat([_load_taipei(), _load_new_taipei()], ignore_index=True)
    if ready_data.empty:
        raise ValueError("No death-cause share data was produced.")

    ready_data = _latest_10_years(ready_data)
    ready_data = ready_data.sort_values(["city", "year", "death_cause"]).reset_index(
        drop=True
    )

    engine = create_engine(ready_data_db_uri)
    _ensure_ready_table(engine)
    save_dataframe_to_postgresql(
        engine,
        data=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, ready_data["data_time"].max())


dag = CommonDag(
    proj_folder="proj_city_dashboard",
    dag_folder="food_safety_death_share",
)
dag.create_dag(etl_func=_transfer)
