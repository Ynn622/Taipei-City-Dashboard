# SQL Init / Seed 問題整理

最後更新：2026-05-10

## 背景

新增 component 或 DAG 後，常會遇到 manager DB 已經有 component/query 設定，但 dashboard data DB 沒有對應資料表或資料，導致 API、圖表或 DAG 執行出錯。

這次 `water_quality` 遇到的問題可以當成通用案例：

- DAG 使用 `load_behavior = replace`。
- `save_geodataframe_to_postgresql()` 會先執行 `TRUNCATE TABLE <table>`。
- 但 `public.water_quality_tpe` / `public.water_quality_ntpe` 尚未在 dashboard data DB 建立。
- Airflow 因此報錯：`relation "water_quality_tpe" does not exist`。

## 重要觀念

專案裡的 `load_stage.py` 不是主要建表機制。多數 `replace` DAG 預期 ready table 已存在。

正常資料表來源通常有幾種：

- `db-sample-data/dashboard-demo.sql`：dashboard data DB 的主要 sample dump。
- `dashboard-demo.sql` 尾端 `\ir ...` include 的資料檔，例如 `food-safety-dashboard-data.sql`。
- 獨立 migration / seed SQL，例如 `add-xxx-data.sql`。
- 少數 DAG 自己寫 `CREATE TABLE IF NOT EXISTS`，但這不是所有 DAG 的通用模式。

Manager DB 和 Dashboard Data DB 是兩件事：

- `dashboardmanager-demo.sql`：component、map config、query chart、dashboard 掛載。
- `dashboard-demo.sql` / include SQL：chart SQL 實際會查的資料表與 seed data。

只補 manager SQL，不補 dashboard data SQL，前端可能有 component，但 API 查資料時會 500。

## 常見症狀

### DAG 失敗

錯誤類型：

```text
psycopg2.errors.UndefinedTable: relation "<table>" does not exist
[SQL: TRUNCATE TABLE <table>]
```

原因：

- `job_config.json` 設定 `load_behavior = replace`。
- ready table 還沒建立。
- loader 先 `TRUNCATE`，所以第一次跑就失敗。

處理：

- 補 dashboard data DB 的 init schema。
- 對已初始化的 running DB，補可直接執行的 `add-xxx-data.sql`。

### 前端看得到，但 DB 沒資料

原因可能是前端地圖和圖表資料來源不同。

以水質為例：

- 地圖：吃 `Taipei-City-Dashboard-FE/public/mapData/water_quality_ntpe.geojson` 靜態 GeoJSON。
- 圖表：原本是 manager DB 裡寫死的 `SELECT unnest(array...)`。
- DB table：DAG 要寫入的 `public.water_quality_ntpe`。

所以即使 DB 沒資料，地圖與圖表仍可能看起來正常。

處理：

- 若圖表要反映 ETL 結果，`query_chart` 應改成查 `public.<ready_table>`。
- 若地圖也要反映 ETL 結果，還需要補 DB 轉 GeoJSON 的流程，或調整前端資料來源。

### 修改 SQL 後畫面沒變

原因：

- Docker volume 已存在。
- 修改 `dashboardmanager-demo.sql` 或 `dashboard-demo.sql` 不會自動套到既有 DB。

處理：

- 已初始化 manager DB：執行對應 `add-xxx-manager.sql`。
- 已初始化 dashboard data DB：執行對應 `add-xxx-data.sql`。
- 或重建 DB volume 後重新跑 init。

## 建議做法

### 1. 先確認 query chart 查什麼

到 `dashboardmanager-demo.sql` 或 migration SQL 找該 component 的 `query_chart`。

如果還是這種寫死資料：

```sql
SELECT unnest(array['A','B']) AS x_axis,
       unnest(array[1,2]) AS data
```

而你希望它跟 DAG / DB 連動，就應改成：

```sql
SELECT name AS x_axis,
       turbidity_ntu::float AS data
FROM public.water_quality_tpe
WHERE turbidity_ntu IS NOT NULL
ORDER BY data DESC, x_axis;
```

雙北或多資料源可用：

```sql
SELECT name AS x_axis,
       turbidity_ntu::float AS data
FROM (
    SELECT name, turbidity_ntu FROM public.water_quality_tpe
    UNION ALL
    SELECT name, turbidity_ntu FROM public.water_quality_ntpe
) d
WHERE turbidity_ntu IS NOT NULL
ORDER BY data DESC, x_axis;
```

### 2. 補 dashboard data DB init schema

如果 component 屬於既有主題頁，可以補到該主題的 include SQL。

水質案例：

- `db-sample-data/food-safety-dashboard-data.sql`

內容包含：

- `CREATE EXTENSION IF NOT EXISTS postgis`
- `DROP TABLE IF EXISTS`
- `CREATE TABLE`
- seed `INSERT`

### 3. 補 running DB migration

對已初始化過的 DB，另外補一份可直接套用的 SQL。

水質案例：

- `db-sample-data/add-water-quality-data.sql`
- `db-sample-data/add-water-quality-manager.sql`

data migration 建議使用：

```sql
CREATE TABLE IF NOT EXISTS public.<table> (...);

INSERT INTO public.<table> (...)
SELECT ...
WHERE NOT EXISTS (SELECT 1 FROM public.<table>);
```

這樣已經有 DAG 資料時，不會重複塞 seed。

### 4. 同步所有會改同一個 component 的 SQL

除了 `dashboardmanager-demo.sql`，還要搜尋是否有其他 update/migration SQL 會覆蓋同一個 `query_chart`。

水質案例同時改了：

- `db-sample-data/dashboardmanager-demo.sql`
- `db-sample-data/add-water-quality-manager.sql`
- `db-sample-data/update-health-office-water-quality-charts-manager.sql`

否則之後套到舊 migration，可能又把查 DB 的 query 改回寫死 array。

## 套用順序

已存在 running DB 時，通常先套 data，再套 manager：

```bash
docker exec -i postgres-data sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db-sample-data/add-xxx-data.sql
docker exec -i postgres-manager sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db-sample-data/add-xxx-manager.sql
```

原因：

- manager query chart 改成查資料表後，API 會立刻開始查 dashboard data DB。
- 如果 data table 還沒建立，component API 可能立刻 500。

## 驗證清單

確認 data table 存在：

```bash
docker exec postgres-data psql -U postgres -d dashboard -P pager=off -c \
  "SELECT COUNT(*) FROM public.<table>;"
```

確認 manager query 已更新：

```bash
docker exec postgres-manager psql -U postgres -d dashboardmanager -P pager=off -c \
  "SELECT city, query_chart FROM public.query_charts WHERE index = '<component_index>';"
```

測試 component API：

```bash
docker exec dashboard-be sh -lc \
  "wget -qO- 'http://127.0.0.1:8080/api/v1/component/<component-id>/chart?city=metrotaipei' | head -c 1000"
```

Airflow DAG 驗證：

- `replace` DAG 不再出現 `TRUNCATE TABLE <table>` 的 `relation does not exist`。
- DAG 跑完後 `COUNT(*)` 有資料。
- `lasttime_in_data` 有更新。

## 檢查清單

- `job_config.json` 的 `ready_data_default_table` 與 chart SQL table 名稱一致。
- dashboard data DB init SQL 有建立 chart SQL 會查的資料表。
- running DB 有對應 `add-xxx-data.sql`。
- manager DB 有對應 `add-xxx-manager.sql`。
- 所有會更新同一 component 的 migration SQL 都同步改過。
- 若前端地圖吃靜態 GeoJSON，要知道它不會自動跟 DB table 同步。
- 若圖表已改查 DB，要確認 seed 或 DAG 資料已存在。
