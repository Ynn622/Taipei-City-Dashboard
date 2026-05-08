# 組件11：有機農場分布

最後更新：2026-05-02

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Component index：`food_source`
- Component id：`307`
- Component 名稱：有機農場分布
- 圖表類型：`DistrictChart`、`TreemapChart`、`BarChart`
- 單位：處

## 目前完成狀態

- 使用臺北市有機農場與新北市有機農場 API。
- 總覽以行政區圖、矩形圖與橫向長條圖呈現各行政區有機農場數量。
- 已掛到 `food_safety_health_tpe` 與 `food_safety_health_metrotaipei` dashboard。

## 地圖圖層

- `food_source_tpe`
  - Map config id：`209`
  - 標題：臺北市有機農場
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_source_tpe.geojson`
  - 目前點位：35 筆
  - 定位方式：21 筆臺北市門牌位置數值資料、14 筆 OpenStreetMap 道路/地名定位
  - 圈圈大小：依 `area_ha` 面積公頃調整

- `food_source_ntpe`
  - Map config id：`210`
  - 標題：新北市有機農場
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_source_ntpe.geojson`
  - 目前點位：298 筆
  - 定位方式：243 筆國土測繪中心地籍宗地圖形中心、25 筆 OpenStreetMap 道路/地名定位、30 筆行政區中心 fallback
  - 圈圈大小：依 `area_ha` 面積公頃調整

## Popup 顯示欄位

### 臺北市有機農場

- 農場名稱：`name`
- 農友/經營者：`operator`
- 縣市：`city`
- 行政區：`district`
- 地址：`address`
- 認證字號：`certification_no`
- 驗證狀態：`certification_status`
- 面積(公頃)：`area_ha`
- 食農教育體驗：`food_education`
- 飼養蜜蜂：`beekeeping`
- 飼養雞隻：`chicken_raising`

### 新北市有機農場

- 農場名稱：`name`
- 農友/經營者：`operator`
- 縣市：`city`
- 行政區：`district`
- 地址：`address`
- 電話：`phone`
- 有效日期：`certification_valid_until`
- 驗證狀態：`certification_status`
- 面積(公頃)：`area_ha`

## 公開資料來源

- 臺北市有機農場
  https://data.taipei/dataset/detail?id=32aea2da-14a7-47b6-a687-57e29c1ad4a7
- 新北市有機農場
  https://data.ntpc.gov.tw/datasets/fc30f585-66d9-4233-a65e-c650d177ebfe

## ETL DAG

- 臺北市：
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_source_tpe/food_source_tpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_source_tpe/job_config.json`

- 新北市：
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_source_ntpe/food_source_ntpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_source_ntpe/job_config.json`

## Seed SQL

- `db-sample-data/add-food-source-manager.sql`

## 目前注意事項

- 新北有機農場多數地址是地號；目前以國土測繪中心段籍清單比對地段代碼，再用地籍圖形回傳範圍計算中心點。
- 仍有 30 筆因非地號地址、段籍代碼查無資料或官方端暫時未產圖而保留行政區中心 fallback。
