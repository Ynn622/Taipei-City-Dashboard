# 組件2：餐飲衛生優良業者分布

最後更新：2026-05-10

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：`food_safety_health_metrotaipei`
- Component index：`fda_good_restaurants`
- Component 名稱：餐飲衛生優良業者分布
- 圖表類型：`DistrictChart`、`RankListChart`、`TreemapChart`
- 單位：家

## 資料定位

此 component 彙整雙北最新年度評核結果為「優」或「良」的餐飲衛生優良業者，作為生活指南與餐飲品質觀察的基礎圖層。

目前資料以最新年度為主，地圖點位存放於：

- `Taipei-City-Dashboard-FE/public/mapData/fda_good_restaurants.geojson`

此 GeoJSON 不再自行重新抓來源資料產生；正式流程以 DAG 寫入的
`public.fda_good_restaurants` 為可信資料來源，再由匯出工具轉成前端靜態圖資。

## DB 資料表

- Airflow DAG：`proj_city_dashboard_fda_good_restaurants`
- Airflow connection：`postgres_default`
- 寫入資料庫：`dashboard`
- Schema：`public`
- 目前資料表：`public.fda_good_restaurants`
- 歷史資料表：`public.fda_good_restaurants_history`
- 載入方式：`current+history`
  - `public.fda_good_restaurants`：每次 DAG 成功執行會清空後寫入最新年度資料。
  - `public.fda_good_restaurants_history`：每次 DAG 成功執行會追加一份當次資料。

## 地圖圖層

- Map config index：`fda_good_restaurants`
- 標題：優良餐廳
- 圖層型態：`circle`
- 資料來源型態：`geojson`
- 實際讀取路徑：`/mapData/fda_good_restaurants.geojson`
- 顏色：
  - `優`：綠色
  - `良`：黃色

## Popup 顯示欄位

- 店名：`restaurant_name`
- 地址：`address`
- 評分結果：`rating_result`
- 年度：`award_year`

## 資料來源

- 新北市食安智慧圖資平台優良餐飲資料
- 臺北市餐飲衛生管理相關開放資料

## 經緯度產生方式

- 新北市：
  - 由新北市 FoodTracer API 直接取得來源提供的 `lon`、`lat`。
  - ETL 只會保留有年度、經度、緯度的資料。
- 臺北市：
  - 臺北市來源 CSV 只提供店名、地址與評核結果，沒有直接提供經緯度。
  - ETL 會先整理地址格式，將 `台北市` 統一為 `臺北市`，並補上縣市前綴。
  - 地址轉座標順序：
    1. 臺北市門牌位置資料：優先做門牌級定位，門牌檔首次使用會下載並快取於本機/container。
    2. TPGOS：若門牌資料未命中，使用專案既有 `get_addr_xy_parallel` 地址轉座標。
    3. Nominatim：若 TPGOS 仍未命中，使用 OpenStreetMap Nominatim 作為道路或地名層級定位備援。
  - 三段定位都未取得座標者，最後會因 `lng`、`lat` 缺值被排除。
- 輸出座標系統：
  - `lng`、`lat` 為 WGS84 / EPSG:4326。
  - 寫入 DB 前會轉成 `wkb_geometry`，幾何型態為 `Point`。

## 相關檔案

- Manager SQL：`db-sample-data/food-safety-good-restaurants-map-layer.sql`
- GeoJSON 匯出工具：`scripts/export_fda_good_restaurants_geojson.py`
- 前端圖資：`Taipei-City-Dashboard-FE/public/mapData/fda_good_restaurants.geojson`
