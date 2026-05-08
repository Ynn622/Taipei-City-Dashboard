# 組件2：餐飲衛生優良業者分布

最後更新：2026-05-03

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

## 地圖圖層

- Map config index：`fda_good_restaurants`
- 標題：優良餐廳
- 圖層型態：`circle`
- 資料來源型態：`geojson`
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

## 相關檔案

- Manager SQL：`db-sample-data/food-safety-good-restaurants-map-layer.sql`
- GeoJSON 產生工具：`scripts/generate_fda_good_restaurants_geojson.py`
- 前端圖資：`Taipei-City-Dashboard-FE/public/mapData/fda_good_restaurants.geojson`
