# 組件9：主要死因死亡占比
最後更新：2026-05-03

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Dashboard id：
  - 臺北市：`401`
  - 雙北：`402`
- Component index：`food_safety_death_share`
- Component id：`503`
- Component 名稱：主要死因死亡占比
- 圖表類型：`TimelineSeparateChart`
- 單位：`%`
- Query type：`time`
- Map config：無獨立點線面圖層

## 指標口徑

此組件統一呈現「死因死亡占比」，不是死亡率。

- 臺北市：使用主要死因死亡率表，計算 `該死因死亡率 / 所有死亡原因死亡率 * 100`
- 新北市：使用主要死因死亡人數表，計算 `該死因死亡人數 / 所有死亡人數 * 100`

臺北死亡率同年度使用相同人口分母，因此相除後可轉為占總死亡比例。新北來源是死亡人數，也可直接用該死因人數除以總死亡人數。兩者轉換後可用 `%` 做口徑一致的呈現。

此指標不可解讀為食安事件直接造成的死亡率，只作為食安健康頁面的慢性病與主要死因背景指標。

## 目前完成狀態

- 已規劃新增 `food_safety_death_share` component，掛到 `food_safety_health_tpe` 與 `food_safety_health_metrotaipei`。
- Component 不新增 `component_maps` 或 FE GeoJSON。
- Dashboard 主圖直接讀最新年度往前 10 年死亡占比趨勢。
- 不另外顯示歷史資料圖。
- 臺北與雙北共用同一張 Dashboard data table：`public.food_safety_death_cause_share`。
- 因占比需呈現小數，BE 時間序列資料解析需維持 `float64`。

## 資料來源

### 臺北市

- 資料：臺北市主要死因死亡率
- API：
  https://tsis.dbas.gov.taipei/statis/webMain.aspx?sys=220&ymf=8100&kind=21&type=0&funid=A05032801&cycle=4&outmode=12&compmode=0&outkind=1&deflst=2&nzo=1
- 年度：2024 - 2014（要轉西元）
- 使用欄位：
  - `死亡率/ 所有死亡原因`
  - `死亡率/ 心臟疾病`
  - `死亡率/ 糖尿病`
  - `死亡率/ 腎炎腎徵候群及腎性病變`
  - `死亡率/ 慢性肝病及肝硬化`

### 新北市

- 資料：死亡人數-主要死因
- 資料頁面：
  https://data.ntpc.gov.tw/datasets/e490f906-93f0-4fc3-b5b3-fe34fb31d1db
- 年度：2024 - 2014
- 使用欄位：
  - `itemvalue2 + itemvalue3`：所有死亡人數
  - `itemvalue6 + itemvalue7`：心臟疾病
  - `itemvalue10 + itemvalue11`：糖尿病
  - `itemvalue14 + itemvalue15`：腎炎腎徵候群及腎性病變
  - `itemvalue20 + itemvalue21`：慢性肝病及肝硬化

## DAG 資料流程

新增 Airflow DAG，放在臺北市 project folder，單一 DAG 同時整理臺北市與新北市資料：

- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_death_share/food_safety_death_share.py`
- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_death_share/job_config.json`

DAG 會打臺北市主計處 CSV 匯出 API 與新北市開放資料 API，計算雙北主要死因死亡占比，並寫入：

- `public.food_safety_death_cause_share`

保留邏輯：

- 每個城市保留最新年度往前 10 年資料。
- `load_behavior` 使用 `replace`，每次 DAG 重新產生完整 10 年主圖時間序列視窗。
- Dashboard 主圖直接讀同一張表的 10 年資料，不再設定獨立歷史圖。

### 臺北轉換邏輯

1. 下載主計處 CSV。
2. 將 `統計期` 由民國年轉西元年。
3. 讀取 4 個目標死因與 `死亡率/ 所有死亡原因`。
4. 逐年度計算：

```text
death_share_percent = cause_mortality_rate / all_cause_mortality_rate * 100
```

### 新北轉換邏輯

1. 使用新北市 CSV API 讀取 `e490f906-93f0-4fc3-b5b3-fe34fb31d1db`。
2. 以男女欄位加總取得所有死亡人數與 4 個目標死因死亡人數。
3. 逐年度計算：

```text
death_share_percent = cause_death_count / all_death_count * 100
```

## 資料表

- `public.food_safety_death_cause_share`

欄位：

- `data_time`
- `year`
- `city`
- `death_cause`
- `metric_basis`：`死亡率` 或 `死亡人數`
- `cause_value`
- `all_cause_value`
- `death_share_percent`

欄位型別重點：

- `year`：integer
- `cause_value`、`all_cause_value`、`death_share_percent`：numeric / float
- `data_time`：DAG 執行時間字串或 timestamp，可供 dataset info 更新使用

## Manager DB 設定

需要新增或更新：

- `component_charts`
  - `index = food_safety_death_share`
  - `types = {TimelineSeparateChart}`
  - `unit = %`
  - 顏色使用 4 個死因對應色
- `components`
  - `id = 503`
  - `index = food_safety_death_share`
  - `name = 主要死因死亡占比`
- `dashboards`
  - `food_safety_health_tpe` 加入 component id `503`
  - `food_safety_health_metrotaipei` 加入 component id `503`
- `query_charts`
  - 臺北市 `city = taipei`
  - 雙北 `city = metrotaipei`
  - `map_config_ids = {}`
  - `history_config = NULL`
  - `map_filter = {}`
  - `query_type = time`
  - `query_history = NULL`

不需要新增：

- `component_maps`
- `Taipei-City-Dashboard-FE/public/mapData/*.geojson`


## Dashboard 整併

需加入：

- `db-sample-data/dashboardmanager-demo.sql`

另提供可套用到既有本機 manager DB 的 SQL：

- Manager DB：`db-sample-data/food-safety-death-share-component.sql`

Dashboard data DB 的 `public.food_safety_death_cause_share` 由 Airflow DAG 產生；為了讓本機 Docker 刪除 volume 後也能直接開啟 503，`db-sample-data/food-safety-dashboard-data.sql` 會保留一份由同來源整理出的 sample seed。

Dashboard query：

- 臺北市：`y_axis` 使用 4 個死因，`x_axis` 使用年度，讀最新年度往前 10 年。
- 雙北：`y_axis` 使用 `死因(台北)` / `死因(新北)`，`x_axis` 使用年度，依各城市最新年度往前讀 10 年，圖例排序為同一死因先台北再新北。
- 不設定 `history_config` 與 `query_history`，避免 UI 顯示歷史資料標籤與彈窗歷史圖。

## 前端調整

`TimelineSeparateChart` 已存在於前端 chart type，不需新增圖表類型。

為了顯示 `14.3%` 這類小數，主圖使用 `query_type = time`，後端既有 `TimeSeriesData.Data` 為 `float64`，可直接支援。

## 注意事項

- 這是死亡占比，不是死亡率。
- 臺北以死亡率換算占比，新北以死亡人數換算占比，兩者結果可以用 `%` 比較。
- 此組件只呈現食安健康相鄰背景，不代表食安直接歸因死亡。
- 臺北資料來源欄位名稱含空白，例如 `死亡率/ 所有死亡原因`，DAG 需做欄位名稱 strip 或容錯查找。
- 新北欄位可能有 `itemvalue2` 或 `item value2` 兩種命名風格，DAG 需以 helper 兼容。
- 若 running manager DB 已存在，只改 `dashboardmanager-demo.sql` 不會自動套用，需執行 `db-sample-data/food-safety-death-share-component.sql`。

## 驗證建議

- Python 語法檢查：

```bash
python -m py_compile Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_death_share/food_safety_death_share.py
```

- SQL 基本檢查：

```bash
psql <manager-db> -f db-sample-data/food-safety-death-share-component.sql
```
