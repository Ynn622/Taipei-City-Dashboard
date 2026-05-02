# 組件5：飲用水/自來水品質（含菌量、軟水、硬水）

最後更新：2026-05-02

## 組件定位

- Component index：`water_quality`
- Component id：`306`
- Component 名稱：淨水場水質
- 圖表類型：`BarChart`
- 單位：NTU
- Dashboard 名稱：食安健康
  - 臺北市：`food_safety_health_tpe`
  - 雙北：`food_safety_health_metrotaipei`

此組件用來在地圖上呈現臺北市與新北市淨水場的飲用水/自來水品質。主要欄位包含菌量相關的大腸桿菌群、pH、濁度、自由有效餘氯、總硬度、總溶解固體量等，可用於觀察水質安全與軟硬水差異。

總覽卡片已移除原本的地圖圖例與矩形圖，只保留橫向長條圖比較各淨水場濁度(NTU)。濁度也是目前地圖圓點大小的依據，適合用來做水質狀態的快速排序比較。

橫向長條圖會依濁度分級上色：

- `< 0.1`：低濁度補位色
- `0.1 - 0.3`：極優
- `0.3 - 0.5`：優良
- `0.5 - 2.0`：合格
- `2.0` 以上：不合格

## 資料來源

### 臺北市

- 資料集：臺北自來水水質檢驗(淨水場清水水質)
- 來源頁面：https://data.taipei/dataset/detail?id=9626c65d-8fe7-45bb-bbe2-7439bed81010
- 實際 CSV 來源：臺北市統計資料庫匯出連結
- 資料型態：年度時間序列統計
- 本次取用邏輯：抓最新年度資料，目前為 `114年度`

### 新北市

- 資料頁面：https://www.water.gov.tw/ch/WaterQuality?nodeId=4631
- 使用方式：在關鍵字欄位查詢 `新北市`
- 資料型態：臺灣自來水公司「平均水質」HTML 頁面
- 本次取用邏輯：
  - 先送出新北市關鍵字查詢。
  - 取得新北市淨水場列表。
  - 再逐一進入每座淨水場明細頁解析測值。
  - 目前解析到 6 座新北市淨水場。

## 地圖圖層

- `water_quality_tpe`
  - Map config id：`207`
  - 標題：臺北市淨水場水質
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/water_quality_tpe.geojson`
  - 目前點位：5 筆

- `water_quality_ntpe`
  - Map config id：`208`
  - 標題：新北市淨水場水質
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/water_quality_ntpe.geojson`
  - 目前點位：6 筆

臺北市 dashboard 只掛 `water_quality_tpe`。雙北 dashboard 同時掛 `water_quality_tpe` 與 `water_quality_ntpe`。

## 水質欄位

兩市資料已整理成共用欄位，方便前端 popup 與後續分析使用：

- 淨水場：`name`
- 英文名稱：`english_name`
- 縣市：`city`
- 行政區：`district`
- 地址：`address`
- 水源：`water_sources`
- 資料時間：`data_time`
- 合格狀態：`qualified`
- pH 值：`ph`
- 濁度(NTU)：`turbidity_ntu`
- 自由有效餘氯(mg/L)：`free_residual_chlorine_mg_l`
- 總硬度(mg/L)：`total_hardness_mg_l`
- 總溶解固體量(mg/L)：`total_dissolved_solids_mg_l`
- 大腸桿菌群(CFU/100mL)：`coliform_cfu_100ml`

其中「含菌量」目前使用 `coliform_cfu_100ml` 呈現；「軟水/硬水」可由 `total_hardness_mg_l` 判斷，數值越高代表水質越偏硬。

## 資料處理流程

### 臺北市處理

1. 從臺北市資料大平臺取得統計 CSV 下載網址。
2. 讀取 CSV 後，以 `統計期` 找出最新年度。
3. 保留最新年度的淨水場清水水質資料。
4. 因同一座淨水場可能有多個水源，依 `淨水場別` 分組彙整。
5. 數值欄位取平均值，例如 pH、濁度、自由有效餘氯、總硬度、總溶解固體量。
6. 水源欄位合併成 `、` 分隔字串。
7. 大腸桿菌群保留來源中的測值文字，例如 `<1`。
8. 加入固定淨水場座標，輸出點位資料。

目前臺北市整理出的 5 座淨水場：

- 公館淨水場
- 直潭淨水場
- 長興淨水場
- 陽明淨水場
- 雙溪淨水場

### 新北市處理

1. 讀取臺灣自來水公司「平均水質」頁面。
2. 取得頁面內的 request verification token。
3. 用 `SearchKeyword=新北市` 送出查詢。
4. 解析搜尋結果中的淨水場名稱、英文名稱、地址、發布日期與明細頁連結。
5. 逐一讀取明細頁表格，抓出需要的水質欄位。
6. 將欄位名稱轉成專案共用英文欄位。
7. 加入固定淨水場座標，輸出點位資料。

目前新北市整理出的 6 座淨水場：

- 貢寮淨水場
- 老梅淨水場
- 林莊淨水場
- 坪林淨水場
- 員山淨水場
- 板新淨水場

## 座標處理

兩市淨水場目前使用固定座標表，而不是每次重新地理編碼。

原因：

- 臺北資料沒有完整地址欄位。
- 新北資料雖有地址，但外部地理編碼對淨水場、山區與郊區地址可能產生漂移。
- 固定座標可避免重跑 DAG 後點位跳動，讓地圖呈現穩定。

固定座標集中在：

- `Taipei-City-Dashboard-DE/dags/utils/water_quality.py`
  - `TAIPEI_PLANT_LOCATIONS`
  - `NEW_TAIPEI_PLANT_LOCATIONS`

## ETL DAG

共用 helper：

- `Taipei-City-Dashboard-DE/dags/utils/water_quality.py`

臺北市 DAG：

- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/water_quality_tpe/water_quality_tpe.py`
- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/water_quality_tpe/job_config.json`

新北市 DAG：

- `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/water_quality_ntpe/water_quality_ntpe.py`
- `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/water_quality_ntpe/job_config.json`

兩個 DAG 都會輸出 PostGIS point geometry，ready table 分別為：

- `water_quality_tpe`
- `water_quality_ntpe`

## Seed SQL 與 Running DB

相關 dashboard、component、map config、query chart 設定已加入：

- `db-sample-data/dashboardmanager-demo.sql`

另外補了一份可直接套用在已初始化 manager DB 的 migration：

- `db-sample-data/add-water-quality-manager.sql`

已設定項目：

- Component chart：`water_quality`
- Component：`306 / water_quality / 淨水場水質`
- Map config：
  - `207 / water_quality_tpe`
  - `208 / water_quality_ntpe`
- Dashboard components：
  - `food_safety_health_tpe`：新增 `306`
  - `food_safety_health_metrotaipei`：新增 `306`
- Query chart：
  - `taipei`：臺北市各淨水場濁度(NTU)
  - `metrotaipei`：雙北各淨水場濁度(NTU)

注意：若 Docker DB volume 已存在，修改 `dashboardmanager-demo.sql` 不會自動影響畫面。需要執行 `db-sample-data/add-water-quality-manager.sql`，或重建 manager DB volume 後重新初始化。

## 前端顯示

前端圖層開關名稱：

- `淨水場水質`

圖層資料：

- 臺北市：`/mapData/water_quality_tpe.geojson`
- 新北市：`/mapData/water_quality_ntpe.geojson`

目前樣式：

- 臺北市：藍色系 `#1E88E5`
- 新北市：青綠色系 `#00A6A6`
- 圓點半徑依 `turbidity_ntu` 進行插值，濁度較高的點位會稍大。

## 驗證紀錄

已完成檢查：

- Python 語法編譯通過。
- 兩份 job config 都是合法 JSON。
- 兩份 GeoJSON 都是合法 JSON。
- 臺北來源可解析出 5 筆淨水場資料。
- 新北來源可用 `新北市` 關鍵字解析出 6 筆淨水場資料。
- 本機 running DB 已套用 `add-water-quality-manager.sql`。
- 後端 API 已確認 `food_safety_health_tpe` 與 `food_safety_health_metrotaipei` 都回傳 `water_quality` component。

## 目前注意事項

- 臺北資料是年度統計值，不是即時測值。
- 新北資料來自臺灣自來水公司頁面，目前解析的是查詢當下明細頁最新發布值。
- `qualified` 欄位在臺北市資料中標示為 `年度均值`，新北市則使用來源頁面的 `Y/N`。
- 若前端看不到「淨水場水質」開關，通常是 manager DB 尚未套用 migration，或瀏覽器需要硬重新整理。
- 若只更新 GeoJSON，通常不需要重啟 Docker；重新整理前端即可重新讀取 `/mapData/*.geojson`。
