# 組件3：食物來源（魚市場、果菜市場、超市）
最後更新：2026-05-02

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Dashboard id：
  - 臺北市：`401`
  - 雙北：`402`
- Component index：`food_safety_market`
- Component id：`303`
- Component 名稱：公有市場圖資
- 圖表類型：`DonutChart`、`TreemapChart`、`BarChart`
- 單位：攤
- 新增 Component index：`food_source`
- 新增 Component id：`307`
- 新增 Component 名稱：食物來源
- 新增圖表類型：`DistrictChart`、`TreemapChart`、`BarChart`
- 新增單位：處

## 目前完成狀態

- 已新增「食安健康」dashboard tab：
  - `food_safety_health_tpe`：臺北市
  - `food_safety_health_metrotaipei`：雙北
- 已把臺北市與新北市公有市場做成 Mapbox circle 圖層。
- 圈圈大小依各市場 `stall_total` 總攤位數決定。
- 點擊市場後會顯示該市場的基本資料與攤位細項。
- 總覽卡片已移除「地圖圖例」，改以圓餅圖、矩形圖與橫向長條圖呈現攤位類型統計。
- 攤位類型會合併為蔬果、肉禽、水產、糧食雜貨、飲食、百貨花卉、其他與空攤；臺北市單城版本不顯示空攤。
- 地圖座標由 OpenStreetMap Nominatim 查詢產生，並先存成前端可讀取的 GeoJSON 靜態檔。
- 已新增「食物來源」component，使用臺北市有機農場與新北市有機農場 API。
- 「食物來源」總覽以行政區圖、矩形圖與橫向長條圖呈現各行政區有機農場數量。
- 「食物來源」已掛到 `food_safety_health_tpe` 與 `food_safety_health_metrotaipei` dashboard。

## 地圖圖層

- `food_safety_market_tpe`
  - Map config id：`201`
  - 標題：臺北市公有市場
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_safety_market_tpe.geojson`
  - 目前已定位點位：45 筆
  - 攤位總數覆蓋：45 筆都有 `stall_total`
  - 圈圈大小：依 `stall_total` 總攤位數調整，無資料時 fallback 為較小預設值

- `food_safety_market_ntpe`
  - Map config id：`202`
  - 標題：新北市公有市場
  - 圖層型態：`circle`
  - 資料來源型態：`geojson`
  - 本機檔案：`Taipei-City-Dashboard-FE/public/mapData/food_safety_market_ntpe.geojson`
  - 目前已定位點位：43 筆
  - 攤位總數覆蓋：31 筆已從統計 ODS 併入 `stall_total`
  - 圈圈大小：依 `stall_total` 總攤位數調整；未對應到統計 ODS 的點位使用固定 fallback 大小

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

### 臺北市

- 市場名稱：`name`
- 行政區：`district`
- 總攤位數：`stall_total`
- 蔬菜攤位：`vegetable_stalls`
- 青果攤位：`fruit_stalls`
- 獸肉攤位：`meat_stalls`
- 漁產攤位：`seafood_stalls`
- 家禽攤位：`poultry_stalls`
- 糧食攤位：`grain_stalls`
- 花卉攤位：`flower_stalls`
- 雜貨攤位：`grocery_stalls`
- 百貨攤位：`general_merchandise_stalls`
- 飲食攤位：`food_stalls`
- 其他攤位：`other_stalls`

### 新北市

- 市場名稱：`name`
- 行政區：`district`
- 總攤位數：`stall_total`
- 果菜攤位：`produce_stalls`
- 畜肉攤位：`meat_stalls`
- 魚蝦攤位：`seafood_stalls`
- 禽肉攤位：`poultry_stalls`
- 糧食攤位：`grain_stalls`
- 雜貨攤位：`grocery_stalls`
- 花卉攤位：`flower_stalls`
- 飲食攤位：`food_stalls`
- 百貨攤位：`general_merchandise_stalls`
- 其他攤位：`other_stalls`
- 空攤：`vacant_stalls`
- 地址：`address`
- 電話：`phone`
- 市場型態：`type`

### 食物來源：臺北市有機農場

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
- 定位方式：`location_method`

### 食物來源：新北市有機農場

- 農場名稱：`name`
- 農友/經營者：`operator`
- 縣市：`city`
- 行政區：`district`
- 地址：`address`
- 電話：`phone`
- 有效日期：`certification_valid_until`
- 驗證狀態：`certification_status`
- 面積(公頃)：`area_ha`
- 定位方式：`location_method`

## 公開資料來源

- 臺北市各區公有零售市(商)場攤位數  
  https://data.taipei/dataset/detail?id=f490476d-d156-4492-a463-cf3405de3b55

- 新北市公有市場名冊  
  https://data.ntpc.gov.tw/datasets/785be91a-caaf-4e1c-91d6-f7d616d31a45

- 新北市各區公有零售市場攤位數  
  新北市統計資訊網，報表 `21412-02-01-2`，目前併入 `114年1月` 報表資料。下載檔案為 ODS，DAG 會從統計頁面找 `DownloadHandler.aspx` 連結後解析。

- 臺北市有機農場
  https://data.taipei/dataset/detail?id=32aea2da-14a7-47b6-a687-57e29c1ad4a7

- 新北市有機農場
  https://data.ntpc.gov.tw/datasets/fc30f585-66d9-4233-a65e-c650d177ebfe

## 新北 ODS 併入邏輯

- ODS 表格提供各市場攤位細項，例如果菜、畜肉、魚蝦、禽肉、糧食、雜貨、花卉、飲食、百貨、其他與空攤。
- DAG 會先整理新北市場名冊，再用市場名稱比對 ODS 攤位資料。
- 成功對應者會寫入 `stall_total` 與各攤位細項欄位。
- 目前 43 筆新北市場點位中有 31 筆成功對應到 ODS 攤位資料；其餘 12 筆仍保留基本資料與座標，但攤位細項為空值。

## ETL DAG

- 臺北市：
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_market_tpe/food_safety_market_tpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_market_tpe/job_config.json`

- 新北市：
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_market_ntpe/food_safety_market_ntpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_market_ntpe/job_config.json`

- 食物來源：臺北市有機農場
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_source_tpe/food_source_tpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_source_tpe/job_config.json`

- 食物來源：新北市有機農場
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_source_ntpe/food_source_ntpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_source_ntpe/job_config.json`

## Seed SQL

相關 dashboard、component、map config、query chart 設定已加入：

- `db-sample-data/dashboardmanager-demo.sql`

已設定項目：

- Dashboard：`food_safety_health_tpe`、`food_safety_health_metrotaipei`
- Component：`food_safety_market`
- Component：`food_source`
- Map config：`food_safety_market_tpe`、`food_safety_market_ntpe`
- Map config：`food_source_tpe`、`food_source_ntpe`
- Map layer counts：臺北市 45 筆、新北市 43 筆
- Query chart stall ratio：
  - 臺北市：百貨花卉 1876、蔬果 1305、糧食雜貨 1067、肉禽 951、飲食 663、水產 621、其他 592
  - 雙北：百貨花卉 2205、蔬果 1659、糧食雜貨 1463、肉禽 1381、飲食 1086、水產 851、其他 848、空攤 144
- Circle paint：
  - 臺北市：綠色系，半徑依 `stall_total` 插值
  - 新北市：橘色系，半徑依 `stall_total` 插值，缺值 fallback 為 80

食物來源也可用獨立 SQL 套用到 running manager DB：

- `db-sample-data/add-food-source-manager.sql`

注意：若本機 Docker DB volume 已經存在，修改 seed SQL 不會自動套用到 running DB，需要重建 manager DB 或手動 upsert 設定。若已手動更新 running DB，通常前端硬重新整理或重新登入即可看到最新 popup 欄位。

## 目前注意事項

- 臺北資料原始欄位沒有地址，點位是用市場名稱加行政區查詢座標。
- 新北資料有地址，但部分「橋下、廟旁、攤販集中場」資料無法穩定由 OpenStreetMap 定位。
- 新北有機農場多數地址是地號；目前以國土測繪中心段籍清單比對地段代碼，再用地籍圖形回傳範圍計算中心點。仍有 30 筆因非地號地址、段籍代碼查無資料或官方端暫時未產圖而保留行政區中心 fallback。
- 新北公有市場名冊本身未提供店家/攤位總數，已另併新北統計 ODS 的 `stall_total`、果菜、畜肉、魚蝦、禽肉、糧食、雜貨、花卉、飲食、百貨、其他、空攤欄位。
- 新北部分市場或攤販集中區未出現在統計 ODS 中，這些點位會保留在地圖上，但攤位數欄位為空並使用固定 fallback 圈圈大小。
- 新北有機農場 API 多數地址為地段地號，若未接地籍圖或地號定位服務，無法穩定轉成精準座標；目前只有街路門牌資料使用 OSM 定位，其餘以行政區中心加偏移呈現，並在 popup 顯示 `location_method`。
- 目前 GeoJSON 已先放入可定位資料，缺漏點位後續可人工補座標或改接更穩定的地理編碼服務。
- 本機 nginx dev config 已補 WebSocket upgrade header，避免 Vite HMR 經 nginx 時連線失敗。

## 本機查看建議

- 若前端已開著但看不到新欄位，先用瀏覽器硬重新整理。
- 若 dashboard/tab 資料沒有更新，確認 manager DB 是否已套用 `db-sample-data/dashboardmanager-demo.sql` 中的新增設定，或對 running DB 執行對應 upsert。
- 若只要把既有 manager DB 的公有市場總覽圖表改成攤位類型統計，可執行 `db-sample-data/update-market-stall-charts-manager.sql`。
- 若只有 GeoJSON 內容變更，通常不需要重啟 Docker；重新整理前端即可重新讀取 `/mapData/*.geojson`。
