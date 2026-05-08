# 組件4：食安健康-腹瀉就診數量統計
最後更新：2026-05-08

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Component index：`cdc_infectious_disease`
- Component id：`502`
- Component 名稱：腹瀉就診數量統計
- 圖表類型：`ColumnLineChart`
- 單位：人次；折線序列為 `%`

## 資料整理

已將 2 份 CDC 腹瀉 CSV 以 pandas 整併為單一週加總大表，資料範圍為 2016 至 2026 年。ETL 寫入資料庫前會先將 `county` 的「台」統一為「臺」，再只保留 `臺北市` 資料。

- 健保門診及住院就診人次統計-腹瀉
  https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv
- 急診傳染病監測統計-急性腹瀉
  https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv
目前 Airflow 寫入 `public.cdc_infectious_disease` 筆數：11,548 筆。

最新資料週別：2026 年第 17 週。週資料的 `data_time` 為該 ISO week 的週一日期，目前最新為 `2026-04-20`。

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
- `diarrhea_visit_rate`

其中 `county` 已將「台」統一為「臺」。component 4 DAG 目前只寫入 `臺北市`，因此資料表中的 `county` 只有 `臺北市`。

`patient_visit` 與 `total_nhi_patient_visit` 已依 ISO week 加總；`data_time` 使用 ISO week 週一日期。

`diarrhea_visit_rate` 計算公式：

```text
腹瀉就診率 = 腹瀉健保就診人次 / 健保就診總人次 * 100
```

## ETL DAG

- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/cdc_infectious_disease/cdc_infectious_disease.py`
- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/cdc_infectious_disease/job_config.json`

Airflow table：

- `public.cdc_infectious_disease`

寫入範圍：

- `county = '臺北市'`

排程：

- 每週二 10:00 更新

## Dashboard 整併

相關 component、chart、query chart 與 dashboard components 設定已加入：

- `db-sample-data/dashboardmanager-demo.sql`

另提供可套用到既有本機 manager DB 的 idempotent SQL：

- `db-sample-data/food-safety-infectious-disease-component.sql`

Dashboard query 設定：

- 臺北市：`county = '臺北市'`
- 雙北：目前資料表僅寫入 `臺北市`，若需要雙北版本，DAG 的寫入範圍需再加入 `新北市`
- 主圖顯示近 12 週資料，圖表為 `ColumnLineChart` 長條折線圖
- 主圖長條 Series：`門診`、`住院`、`急診`，以堆疊直條呈現，數值為原始人次
- 主圖折線 Series：`腹瀉就診率`
- 點開組件後的歷史圖以年為單位加總，顯示 2016 至 2026 年年度趨勢
- 歷史圖 Series：`門診`、`住院`、`急診`
