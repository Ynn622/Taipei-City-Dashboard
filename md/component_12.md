# 組件12：食品過敏原風險分類

最後更新：2026-05-03

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Component index：`food_allergen_classification`
- Component id：`504`
- Component 名稱：食品過敏原風險分類
- 圖表類型：`MapLegend`、`DonutChart`
- 單位：項

## 指標定位

此 component 以食品成分資料為基礎，透過分類結果標註產品是否含有特殊過敏原，並以品牌或公司定位後呈現在地圖上。

分類標籤包含：

- 乳製品
- 海鮮類
- 麩質穀物
- 花生
- 酒精
- 蠶豆

## 地圖圖層

- `food_allergen_classification_tpe`
  - 標題：臺北市食品過敏原分布
  - 圖層型態：`circle`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_allergen_classification_tpe.geojson`

- `food_allergen_classification_metrotaipei`
  - 標題：雙北食品過敏原分布
  - 圖層型態：`circle`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_allergen_classification_metrotaipei.geojson`

顏色：

- 含過敏原：紅色
- 不含過敏原：綠色

## Popup 顯示欄位

- 縣市：`county`
- 公司名稱：`company_name`
- 品牌名稱：`brand_name`
- 產品名稱：`product_name`
- 是否含過敏原：`has_allergens`
- 過敏原清單：`allergens`

## ETL DAG

- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_allergen_classification/food_allergen_classification.py`
- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_allergen_classification/job_config.json`

## Seed SQL

- `db-sample-data/add-food-allergen-classification.sql`

## 注意事項

- 此資料是產品層級資料，圖表單位使用 `項`。
- 地圖定位依品牌或公司資訊進行地理編碼，需保留無法定位資料的稽核路徑。
