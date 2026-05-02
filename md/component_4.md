# 組件4：食安健康-腹瀉就診數量統計
最後更新：2026-05-02

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Component index：`cdc_infectious_disease`
- Component id：`502`
- Component 名稱：腹瀉就診數量統計
- 圖表類型：`ColumnChart`
- 單位：人次

## 資料整理

已將 2 份 CDC 腹瀉 CSV 以 pandas 整併為單一週加總大表，資料範圍為 2016 至 2026 年。腸病毒資料已移除。

- 健保門診及住院就診人次統計-腹瀉  
  https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv
- 急診傳染病監測統計-急性腹瀉  
  https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv
本機輸出檔：

- `Taipei-City-Dashboard-DE/data/cdc_infectious_disease_combined.csv`

目前輸出筆數：238,637 筆。

最新資料週別：2026 年第 16 週。週資料的 `data_time` 為該 ISO week 的週一日期，目前最新為 `2026-04-13`。

## 統一欄位

- `data_time`
- `year`
- `week`
- `dataset_name`
- `surveillance_type`
- `disease_group`
- `disease_name`
- `visit_type`
- `age_group`
- `county`
- `county_code`
- `patient_visit`
- `total_nhi_patient_visit`

其中 `county` 已將「台」統一為「臺」，方便 dashboard query 用 `臺北市`、`新北市` 過濾。

`patient_visit` 與 `total_nhi_patient_visit` 已依 ISO week 加總；`data_time` 使用 ISO week 週一日期。

## ETL DAG

- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/cdc_infectious_disease/cdc_infectious_disease.py`
- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/cdc_infectious_disease/job_config.json`

Airflow table：

- `public.cdc_infectious_disease`

排程：

- 每週二 10:00 更新

## Dashboard 整併

相關 component、chart、query chart 與 dashboard components 設定已加入：

- `db-sample-data/dashboardmanager-demo.sql`

另提供可套用到既有本機 manager DB 的 idempotent SQL：

- `db-sample-data/food-safety-infectious-disease-component.sql`

Dashboard query 設定：

- 臺北市：`county = '臺北市'`
- 雙北：`county IN ('臺北市', '新北市')`
- 主圖顯示近 12 週資料，圖表為 `ColumnChart` 縱向長條圖
- 主圖 Series：`門診`、`住院`、`急診`
- 點開組件後的歷史圖以年為單位加總，顯示 2016 至 2026 年年度趨勢
- 歷史圖 Series：`門診`、`住院`、`急診`

## 本機 CSV 重新產生

若已有 2 個原始 CSV，可指定資料夾：

```bash
python scripts/generate_cdc_infectious_disease_csv.py --input-dir /path/to/raw-csv-dir --output Taipei-City-Dashboard-DE/data/cdc_infectious_disease_combined.csv
```

若未指定 `--input-dir`，腳本會直接從 CDC URL 讀取資料。
