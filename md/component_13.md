# 組件13：農產品產銷履歷不合格率

## Dashboard 設定

- **Component**：`506 / agri_sales_resume_noncompliance / 農產品產銷履歷不合格率`
- **Chart**：`TimelineSeparateChart`
- **Chart 維度**：`y_axis = '不合格率'`（單一折線）
- **Unit**：`%`
- **Map layers**：無

---

## 資料來源

| 欄位 | 說明 |
|------|------|
| API | `https://data.moa.gov.tw/api/v1/SalesResumeAgriproductsResultsType/` |
| 主管機關 | 農業部農糧署 |
| 資料覆蓋 | 全台（無地區篩選需求） |
| 更新頻率 | 資料持續新增，建議每週一抓取 |

### API 回傳格式

```json
{
  "RS": "OK",
  "Data": [
    {
      "Number": "TGAP1140500065",
      "SamplingDate": "1141211",
      "ProductName": "茭白筍-履歷茭白筍",
      "ProductID": "2511200007905592",
      "ProducerName": "陳泰銓",
      "SamplingLocation": "臺南市中西區中華西路二段16號",
      "InspectResult": "標示合格",
      "Note": "品質不合格(不符合容許量及未核准用藥)"
    }
  ]
}
```

### InspectResult 值域（已觀察）

| 值 | 意義 |
|----|------|
| `合格` | 標示與品質均合格 |
| `標示合格` | 標示合格但品質不合格（Note 欄有說明） |
| `不合格` | 完全不合格（預期存在） |

> **判定規則**：`InspectResult == '合格'` → pass；其他一律 → noncompliant

### API 分頁

- 參數：`?Page=1`
- 無 total count，以 `Data` 陣列為空或 `RS != 'OK'` 為止循環
- `Next` 可能誤報，ETL 需保留重複頁防呆，避免無限抓取同一頁

---

## ETL 策略

1. **全量爬取**：每次執行分頁抓取全部資料（API 無歷史過濾機制，全量 replace）
2. **日期轉換**：`SamplingDate` 格式為民國 `YYYMMDD`（7碼），轉 Gregorian：
   - `year = int(date_str[:3]) + 1911`
   - `month = int(date_str[3:5])`
   - 組成 `YYYY-MM-01` 作為月份 x_axis
3. **不合格判定**：`InspectResult != '合格'` → 不合格
4. **聚合**：按月份統計 `total_count`（總件數）與 `noncompliant_count`（不合格數）
5. **不合格率**：`noncompliant_count / total_count * 100`，保留 2 位小數
6. **load_behavior**：`replace`（每次全量覆蓋）

---

## DB Schema

```sql
-- 建於 postgres-data
CREATE TABLE IF NOT EXISTS public.agri_sales_resume_noncompliance (
    sample_month       date,
    total_count        int,
    noncompliant_count int,
    noncompliance_rate float
);
```

---

## Query SQL（前端顯示）

```sql
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
```

---

## 組件設定（Manager DB）

| 欄位 | 值 |
|------|----|
| `id` | `506` |
| `index` | `agri_sales_resume_noncompliance` |
| `name` | `農產品產銷履歷不合格率` |
| `chart types` | `TimelineSeparateChart` |
| `color` | `['#ED6A45']` |
| `unit` | `%` |
| `update_freq` | `1` |
| `update_freq_unit` | `week` |
| `source` | `農業部農糧署` |
| `query_type` | `time` |
| `city` | `taipei`, `metrotaipei` |

---

## 需建立的檔案

| 路徑 | 說明 |
|------|------|
| `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/agri_sales_resume_noncompliance/__init__.py` | 空白 |
| `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/agri_sales_resume_noncompliance/agri_sales_resume_noncompliance.py` | DAG 主程式 |
| `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/agri_sales_resume_noncompliance/job_config.json` | Airflow 設定 |
| `db-sample-data/add-agri-sales-resume-noncompliance.sql` | Manager + Data 初始化 SQL |

---

## DAG job_config.json 規格

```json
{
  "dag_infos": {
    "dag_id": "agri_sales_resume_noncompliance",
    "start_date": "2026-05-03",
    "schedule_interval": "0 2 * * 1",
    "catchup": false,
    "tags": ["moa", "食安健康", "農產品", "產銷履歷", "不合格率"],
    "description": "Weekly crawl of agricultural product sales resume inspection results; compute monthly non-compliance rate.",
    "default_args": {
      "owner": "airflow",
      "email": ["DEFAULT_EMAIL_LIST"],
      "email_on_retry": false,
      "email_on_failure": true,
      "retries": 1,
      "retry_delay": 60
    },
    "ready_data_db": "postgres_default",
    "ready_data_default_table": "agri_sales_resume_noncompliance",
    "ready_data_history_table": "",
    "raw_data_db": "postgres_default",
    "raw_data_table": "",
    "load_behavior": "replace"
  },
  "data_infos": {
    "name_cn": "食安健康-農產品產銷履歷不合格率",
    "airflow_update_freq": "02:00 every Monday",
    "source": "https://data.moa.gov.tw/api/v1/SalesResumeAgriproductsResultsType/",
    "source_type": "MOA Open API",
    "source_dept": "農業部農糧署",
    "gis_format": "",
    "output_coordinate": "",
    "is_geometry": 0,
    "dataset_description": "農業部農糧署產銷履歷農產品抽驗結果，涵蓋全台各縣市抽驗紀錄，計算各月不合格率。",
    "etl_description": "分頁爬取 MOA API 全量資料，依 InspectResult 欄位判定合格/不合格，按月份聚合計算不合格率後寫入 agri_sales_resume_noncompliance table。",
    "sensitivity": "public"
  }
}
```

---

## ETL 注意事項

1. **民國轉西元**：`SamplingDate` 為 7 碼字串，前 3 碼為民國年，須 +1911
2. **API 無 total 欄位**：需以 `Page` 方式分頁，並在空資料、`RS != 'OK'` 或重複頁時停止
3. **不合格定義**：InspectResult 非「合格」即視為不合格
4. **空月份**：若某月無資料可跳過，不補零
5. **請求速率**：建議 `time.sleep(0.5)` 避免被擋

---

## Verification Checklist

- [ ] DAG 執行成功，`agri_sales_resume_noncompliance` table 有資料
- [ ] `sample_month` 日期格式正確（西元 YYYY-MM-01）
- [ ] `noncompliance_rate` 數值合理（0~100%）
- [ ] Manager DB 組件 ID 506 正確插入
- [ ] 前端 `TimelineSeparateChart` 顯示不合格率折線
- [ ] 組件掛入對應 dashboard

---

## 相關檔案

- DAG：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/agri_sales_resume_noncompliance/`
- Manager + Data SQL：`db-sample-data/add-agri-sales-resume-noncompliance.sql`
- 參考組件：`food_processing_pass_rate`（相似 TimelineSeparateChart 架構）
