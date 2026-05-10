# 組件3：公有市場圖資
最後更新：2026-05-10

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

## 目前完成狀態

- 已新增「食安健康」dashboard tab：
  - `food_safety_health_tpe`：臺北市
  - `food_safety_health_metrotaipei`：雙北
- 已把臺北市與新北市公有市場做成 Mapbox circle 圖層。
- 圈圈大小依各市場 `stall_total` 總攤位數決定。
- 點擊市場後會顯示該市場的基本資料與攤位細項。
- 總覽卡片已移除「地圖圖例」，改以圓餅圖、矩形圖與橫向長條圖呈現攤位類型統計。
- 攤位類型會合併為蔬果、肉禽、水產、糧食雜貨、飲食、百貨花卉、其他與空攤；臺北市單城版本不顯示空攤。
- 臺北市地圖座標優先使用「臺北市公有市場」CSV 內的 `GTag_longitude`、`GTag_latitude`，缺漏時才 fallback TPGOS 查詢；前端另存成可讀取的 GeoJSON 靜態檔。
- 新北市地圖座標依序使用 TPGOS、OpenStreetMap Nominatim 與行政區中心補值，避免橋下、廟旁、攤販集中場等地址定位失敗時整筆資料被丟棄。

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

## 公開資料來源

- 臺北市各區公有零售市(商)場攤位數
  https://data.taipei/dataset/detail?id=f490476d-d156-4492-a463-cf3405de3b55

- 新北市公有市場名冊
  https://data.ntpc.gov.tw/datasets/785be91a-caaf-4e1c-91d6-f7d616d31a45

- 新北市各區公有零售市場攤位數
  新北市統計資訊網發布頁，DAG 會用前一年 `12/25` 發布頁尋找標題為「新北市各區公有零售市場攤位數.ods」的 `DownloadHandler.aspx` 連結後下載解析。

## 新北 ODS 併入邏輯

- ODS 表格提供各市場攤位細項，例如果菜、畜肉、魚蝦、禽肉、糧食、雜貨、花卉、飲食、百貨、其他與空攤。
- DAG 會先整理新北市場名冊，再用行政區與標準化後的市場名稱比對 ODS 攤位資料。
- 成功對應者會寫入 `stall_total` 與各攤位細項欄位。
- 目前 43 筆新北市場點位中有 31 筆成功對應到 ODS 攤位資料；其餘 12 筆仍保留基本資料與座標，但攤位細項為空值。

## 新北定位邏輯

- 名冊地址會先補齊「新北市 + 行政區」，再經 `clean_data`、`main_process`、`save_data` 做地址標準化。
- 第一順位使用 `get_addr_xy_parallel` 查 TPGOS，成功者標記為 `地址轉座標`。
- TPGOS 未命中者改用 `utils.nominatim_geocoder.geocode_addresses_with_osm` 查 OpenStreetMap Nominatim，成功者標記為 `OpenStreetMap道路/地名定位`。
- 仍缺座標者使用 `utils.district_geocoder.DISTRICT_CENTROIDS` 依行政區中心補點，標記為 `行政區中心`。
- 若三段流程後仍有缺漏座標，DAG 會直接拋錯，避免悄悄寫入不完整圖資。

## ETL DAG

- 臺北市：
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_market_tpe/food_safety_market_tpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_market_tpe/job_config.json`

- 新北市：
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_market_ntpe/food_safety_market_ntpe.py`
  - `Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_market_ntpe/job_config.json`

## Seed SQL

相關 dashboard、component、map config、query chart 設定已加入：

- `db-sample-data/dashboardmanager-demo.sql`

已設定項目：

- Dashboard：`food_safety_health_tpe`、`food_safety_health_metrotaipei`
- Component：`food_safety_market`
- Map config：`food_safety_market_tpe`、`food_safety_market_ntpe`
- Map layer counts：臺北市 45 筆、新北市 43 筆
- Query chart stall ratio：
  - 臺北市：百貨花卉 1876、蔬果 1305、糧食雜貨 1067、肉禽 951、飲食 663、水產 621、其他 592
  - 雙北：百貨花卉 2205、蔬果 1659、糧食雜貨 1463、肉禽 1381、飲食 1086、水產 851、其他 848、空攤 144
- Circle paint：
  - 臺北市：綠色系，半徑依 `stall_total` 插值
  - 新北市：橘色系，半徑依 `stall_total` 插值，缺值 fallback 為 80

注意：若本機 Docker DB volume 已經存在，修改 seed SQL 不會自動套用到 running DB，需要重建 manager DB 或手動 upsert 設定。若已手動更新 running DB，通常前端硬重新整理或重新登入即可看到最新 popup 欄位。

## 目前注意事項

- 臺北攤位數資料原始欄位沒有地址，DAG 會另併「臺北市公有市場」CSV 的地址與經緯度；缺漏點位才用市場名稱加行政區查詢 TPGOS。
- 新北資料有地址，但部分「橋下、廟旁、攤販集中場」資料無法穩定由 OpenStreetMap 定位。
- 新北公有市場名冊本身未提供店家/攤位總數，已另併新北統計 ODS 的 `stall_total`、果菜、畜肉、魚蝦、禽肉、糧食、雜貨、花卉、飲食、百貨、其他、空攤欄位。
- 新北部分市場或攤販集中區未出現在統計 ODS 中，這些點位會保留在地圖上，但攤位數欄位為空並使用固定 fallback 圈圈大小。
- 新北行政區中心補點只保留概略位置，適合確保資料完整呈現；若需要精準點位，仍建議後續人工補座標或改接更穩定的地理編碼服務。
- 本機 nginx dev config 已補 WebSocket upgrade header，避免 Vite HMR 經 nginx 時連線失敗。

## 本機查看建議

- 若前端已開著但看不到新欄位，先用瀏覽器硬重新整理。
- 若 dashboard/tab 資料沒有更新，確認 manager DB 是否已套用 `db-sample-data/dashboardmanager-demo.sql` 中的新增設定，或對 running DB 執行對應 upsert。
- 若只要把既有 manager DB 的公有市場總覽圖表改成攤位類型統計，可執行 `db-sample-data/update-market-stall-charts-manager.sql`。
- 若只有 GeoJSON 內容變更，通常不需要重啟 Docker；重新整理前端即可重新讀取 `/mapData/*.geojson`。
