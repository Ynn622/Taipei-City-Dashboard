# 組件6：事前稽查【衛生所(局) / 衛生所(局) 地點】

最後更新：2026-05-02

## 組件定位

- 組件6：事前稽查
  - Component index：`food_safety_health_office`
  - Component id：`305`
  - Component 名稱：衛生局
  - 資料主題：雙北衛生局、衛生所與健康服務中心據點
  - 呈現方式：每一個衛生局所屬據點一個地圖點
  - 總覽圖表：`DonutChart`、`TreemapChart`、`BarChart`
  - 總覽單位：處
- Dashboard 名稱：食安健康
  - 臺北市：`food_safety_health_tpe`
  - 雙北：`food_safety_health_metrotaipei`

## 使用情境

此組件用於食安事件的事前稽查與應變支援，讓使用者可以在地圖上快速確認雙北衛生局、衛生所與健康服務中心的位置。

總覽卡片已移除原本的地圖圖例，改以圓餅圖、矩形圖與橫向長條圖呈現據點類型統計：

- 臺北市：健康服務中心 12 處、衛生局 1 處
- 雙北：衛生所 29 處、健康服務中心 12 處、衛生局 2 處

可搭配組件1「物流廠商」與組件3「食物來源」一起使用：

- 事前稽查：確認食品物流業者、市場與衛生局所屬據點的空間關係。
- 稽查派案：依據市場、物流業者所在地，找到鄰近的衛生局、衛生所或健康服務中心。
- 事件應變：食安事件發生時，快速掌握附近可支援的衛生服務據點。
- 資源配置：比較各行政區食品風險點位與衛生稽查支援據點的覆蓋狀況。

## 地圖圖層

- `food_safety_health_office_tpe`
  - Map config id：`205`
  - 標題：臺北市衛生局與健康服務中心
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_safety_health_office_tpe.geojson`
  - 目前點位：13 筆
  - 點位內容：臺北市政府衛生局 1 筆、臺北市各區健康服務中心 12 筆

- `food_safety_health_office_ntpe`
  - Map config id：`206`
  - 標題：新北市衛生局與衛生所
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_safety_health_office_ntpe.geojson`
  - 目前點位：30 筆
  - 點位內容：新北市政府衛生局 1 筆、新北市各區衛生所 29 筆

## 衛生局點位細節

### 臺北市政府衛生局

- 名稱：臺北市政府衛生局
- 類型：衛生局
- 地址：臺北市信義區市府路1號
- 電話：`(02)27208889`
- 網站：https://health.gov.taipei/
- 座標來源：臺北市門牌位置數值資料
- 目前座標：`121.563784, 25.037523`

### 新北市政府衛生局

- 名稱：新北市政府衛生局
- 類型：衛生局
- 地址：新北市板橋區英士路192-1號
- 電話：`(02)22577155`
- 網站：https://www.health.ntpc.gov.tw/
- 座標來源：同址衛生所定位
- 目前座標：`121.4594425, 25.0238847`

## 圖層樣式

- 臺北市圖層顏色：綠色系 `#2F7D6D`
- 新北市圖層顏色：紅色系 `#C2573E`
- 一般衛生所/健康服務中心圓點半徑：`7`
- 衛生局本體圓點半徑：`11`
- 判斷欄位：`agency_type`
  - `衛生局`：顯示較大圓點
  - `衛生所`、`健康服務中心`：顯示一般圓點

目前 Mapbox paint 設定使用 `case` expression，依 `agency_type` 決定圓點大小，因此衛生局本體會比衛生所與健康服務中心更醒目。

## Popup 顯示欄位

### 臺北市

- 名稱：`name`
- 類型：`agency_type`
- 縣市：`city`
- 行政區：`district`
- 地址：`address`
- 電話：`phone`
- 網址：`website`

### 新北市

- 名稱：`name`
- 類型：`agency_type`
- 縣市：`city`
- 行政區：`district`
- 地址：`address`
- 電話：`phone`
- 分機：`extension`
- 郵遞區號：`zipcode`
- 服務時間：`open_time`

## 資料來源

- 臺北市健康服務中心
  https://data.gov.tw/dataset/121146

- 新北市各區衛生所
  https://data.gov.tw/dataset/125693

- 臺北市政府衛生局
  https://health.gov.taipei/

- 新北市政府衛生局
  https://www.health.ntpc.gov.tw/

## ETL 與資料處理

- 共用 helper：
  - `Taipei-City-Dashboard-DE/dags/utils/health_office.py`
- 臺北市 DAG：
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_health_office_tpe/food_safety_health_office_tpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_health_office_tpe/job_config.json`
- 新北市 DAG：
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_health_office_ntpe/food_safety_health_office_ntpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_health_office_ntpe/job_config.json`

定位方式：

- 臺北市健康服務中心與臺北市政府衛生局優先使用臺北市門牌位置數值資料定位。
- 臺北市若門牌資料未命中，會再嘗試專案既有地址轉座標與 OpenStreetMap。
- 新北市衛生所主要使用 OpenStreetMap 道路/地名定位。
- 新北市政府衛生局目前固定在英士路 192/192-1 號這組衛生局所位置，避免重跑 DAG 時因外部地理編碼結果漂移。

## Seed SQL

相關設定已放在：

- `db-sample-data/dashboardmanager-demo.sql`

已設定項目：

- Component：`food_safety_health_office`
- Map config：
  - `205` / `food_safety_health_office_tpe`
  - `206` / `food_safety_health_office_ntpe`
- Dashboard：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Query chart：
  - 臺北市：健康服務中心 12、衛生局 1
  - 雙北：衛生所 29、健康服務中心 12、衛生局 2

## 目前注意事項

- 此組件目前是食安健康 tab 下的「衛生局」component，用於支援事前稽查情境。
- `agency_type` 是前端判斷圓點大小的重要欄位，衛生局本體必須維持為 `衛生局`。
- GeoJSON 變更後通常不需要重啟 Docker，硬重新整理前端即可重新讀取 `/mapData/*.geojson`。
- 若 dashboard component 或圖例沒有更新，需確認 running DB 是否已套用最新 seed SQL 或手動 update。
