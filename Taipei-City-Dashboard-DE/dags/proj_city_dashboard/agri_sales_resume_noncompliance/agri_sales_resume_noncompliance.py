from airflow import DAG
from operators.common_pipeline import CommonDag

API_URL = "https://data.moa.gov.tw/api/v1/SalesResumeAgriproductsResultsType/"


def _agri_sales_resume_noncompliance(**kwargs):
    import time
    import urllib3
    from datetime import date
    from typing import Optional

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.load_stage import (
        save_dataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )

    # 抑制 verify=False 產生的 InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ── 1. 全量分頁爬取 ──────────────────────────────────────────────────────
    all_records = []
    page = 1
    seen_page_signatures = set()

    while True:
        resp = requests.get(
            API_URL,
            params={"Page": page},
            timeout=30,
            verify=False,
        )
        resp.raise_for_status()
        payload = resp.json()

        # RS 不正常代表沒有更多資料或 API 回傳錯誤，避免 Next 誤報造成無限迴圈。
        rs = payload.get("RS", "OK")
        if rs not in ("OK", None, ""):
            print(f"[WARN] API RS={rs!r} at page={page}, stopping.")
            break

        batch = payload.get("Data", [])
        if not batch:
            print(f"[INFO] Empty Data at page={page}, stopping.")
            break

        page_signature = (
            batch[0].get("Number"),
            batch[-1].get("Number"),
            len(batch),
        )
        if page_signature in seen_page_signatures:
            print(f"[WARN] Duplicate page detected at page={page}, stopping.")
            break
        seen_page_signatures.add(page_signature)

        all_records.extend(batch)
        print(f"[INFO] Fetched {len(batch)} records (page={page}), total={len(all_records)}")

        # 使用 API 提供的 Next 欄位判斷是否還有下一頁，但上方仍保留防呆。
        has_next = payload.get("Next", False)
        if not has_next:
            break

        page += 1
        time.sleep(0.5)

    if not all_records:
        raise ValueError("No data returned from MOA API.")

    # ── 2. 轉換 DataFrame ────────────────────────────────────────────────────
    df = pd.DataFrame(all_records)[["SamplingDate", "InspectResult"]]

    # 過濾格式異常的日期（需要 7 碼：YYYMMDD）
    df = df[df["SamplingDate"].str.len() == 7].copy()

    # 民國 YYYMMDD → 西元月份（date(YYYY, MM, 1)）
    # 注意：date | None 為 Python 3.10+ 語法，此處改用 Optional[date]
    def roc_to_month(roc_str):  # type: (str) -> Optional[date]
        try:
            year = int(roc_str[:3]) + 1911
            month = int(roc_str[3:5])
            return date(year, month, 1)
        except (ValueError, TypeError):
            return None

    df["sample_month"] = df["SamplingDate"].apply(roc_to_month)
    df = df.dropna(subset=["sample_month"])

    # ── 3. 不合格判定：InspectResult 非「合格」均視為不合格 ──────────────────
    # 涵蓋：「不合格」「標示合格（品質不合格）」「品質合格（標示不合格）」等
    df["is_noncompliant"] = df["InspectResult"].str.strip() != "合格"

    # ── 4. 按月份聚合 ────────────────────────────────────────────────────────
    monthly = (
        df.groupby("sample_month")
        .agg(
            total_count=("is_noncompliant", "count"),
            noncompliant_count=("is_noncompliant", "sum"),
        )
        .reset_index()
    )

    monthly["noncompliance_rate"] = (
        monthly["noncompliant_count"] / monthly["total_count"] * 100
    ).round(2)

    ready_data = monthly.sort_values("sample_month").reset_index(drop=True)
    print(f"[INFO] Aggregated {len(ready_data)} months of data")
    print(ready_data.to_string())

    # ── 5. 寫入 DB ───────────────────────────────────────────────────────────
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
    proj_folder="proj_city_dashboard",
    dag_folder="agri_sales_resume_noncompliance",
)
dag.create_dag(etl_func=_agri_sales_resume_noncompliance)
