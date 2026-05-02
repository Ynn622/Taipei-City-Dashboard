# 組件1：物流廠商（FDA 食品業者登錄）

最後更新：2026-05-02

## 組件定位

- 組件1：物流廠商
  - Component index：`food_safety_logistics_vendor`
  - Component id：`304`
  - 資料主題：FDA 食品業者登錄中的「物流業」業者
  - 呈現方式：每一筆物流業者一個地圖點
  - 總覽圖表：`DonutChart`、`TreemapChart`、`BarChart`
  - 總覽單位：家
- 組件3：食物來源（魚市場、果菜市場、超市）
  - 文件：`md/component_3.md`
  - Component index：`food_safety_market`
  - Component id：`303`
  - 資料主題：公有市場與市場攤位分類資料

## 來源頁面

- 臺北市食品業者登錄列表  
  https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=%E8%87%BA%E5%8C%97%E5%B8%82

- 新北市食品業者登錄列表  
  https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=%E6%96%B0%E5%8C%97%E5%B8%82

- 食品業者地圖查詢頁  
  https://fadenbook.fda.gov.tw/pub/search-Vendor-Map.aspx

## 可用端點整理

### 1. 縣市列表端點

```txt
GET https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?req=getlist
```

這個端點是縣市列表頁背後使用的查詢端點，但回傳格式是 HTML 表格片段，不是 JSON。

常用參數：

- `city`：縣市名稱，例如 `臺北市`、`新北市`
- `Page`：頁碼
- `Size`：每頁筆數，頁面可選 10、20、30、40
- `tp`：登錄類別，`0` 代表全部

`tp` 分類：

- `0`：全部
- `1`：食品公司
- `2`：食品工廠
- `3`：餐飲
- `4`：通路
- `6`：物流業

範例：

```txt
https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?req=getlist&city=臺北市&Page=1&Size=40&tp=0
```

目前觀察：

- 臺北市列表頁顯示約 98,216 筆。
- 這個端點資料較完整，但沒有直接提供經緯度。
- 若要拿來上地圖，需要再用地址做地理編碼。

## 本次開發：雙北物流業

目前先只抓 `tp=6` 物流業，不抓全部分類。

正式資料處理依照專案 DAG 架構開發，不以 CSV 作為來源。DAG 會直接呼叫 FDA 縣市列表端點，解析 HTML 表格後輸出每一筆物流業者資料。

ETL DAG：

- 臺北市：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_safety_logistics_vendor_tpe/food_safety_logistics_vendor_tpe.py`
- 新北市：`Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_safety_logistics_vendor_ntpe/food_safety_logistics_vendor_ntpe.py`
- 共用 FDA helper：`Taipei-City-Dashboard-DE/dags/utils/fda_food_vendor.py`

前端地圖 GeoJSON：

- 臺北市：`Taipei-City-Dashboard-FE/public/mapData/food_safety_logistics_vendor_tpe.geojson`
- 新北市：`Taipei-City-Dashboard-FE/public/mapData/food_safety_logistics_vendor_ntpe.geojson`

食安健康 tab 設定：

- 新增 component：`food_safety_logistics_vendor`
- 新增 map config：
  - `203` / `food_safety_logistics_vendor_tpe`
  - `204` / `food_safety_logistics_vendor_ntpe`
- 已掛到 dashboard：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`

目前抓取筆數：

- 臺北市：256 筆
- 新北市：479 筆
- 雙北合計：735 筆

總覽卡片呈現：

- 已移除原本的地圖圖例圖表。
- 改以圓餅圖、矩形圖與橫向長條圖呈現各行政區物流業者數量。
- 臺北市版本使用 12 個臺北市行政區。
- 雙北版本合併臺北市與新北市行政區，依業者數由多到少排序。

地圖呈現方式：

- FDA 縣市列表端點沒有提供經緯度。
- 目前地圖以每筆業者顯示一個點；臺北市 DAG 會先用臺北市門牌位置數值資料做門牌級定位，未命中者再嘗試專案既有 TPGOS 地址轉座標、OpenStreetMap Nominatim 道路/地名層級定位，最後才使用行政區中心點加微小偏移。
- 臺北市門牌位置數值資料來源：`https://data.taipei/dataset/detail?id=b7c8e724-1e98-45ee-a0bd-f3840623ed97`。
- 臺北市門牌位置數值資料欄位包含：省市縣市代碼、鄉鎮市區代碼、村里、鄰、街路段、地區、巷、弄、號、橫座標、縱座標。
- 臺北市門牌資料座標為 TWD97，DAG 會轉成 WGS84 後輸出給 Mapbox。
- OpenStreetMap 對台灣門牌通常無法穩定精準到號，因此物流業者多數是「道路/地名定位」，不是 FDA 原始資料提供經緯度。
- 每一點代表一筆物流業者。
- 臺北市 GeoJSON 目前有 256 個業者點位。
- 新北市 GeoJSON 目前有 479 個業者點位。
- 目前臺北市 144 筆使用臺北市門牌位置數值資料定位，112 筆使用 OpenStreetMap 道路/地名定位；新北市 477 筆使用 OpenStreetMap 道路/地名定位，2 筆保留行政區中心微偏移。

目前定位順序：

1. 臺北市門牌位置數值資料：只用於臺北市，能命中時可到門牌級。
2. 專案既有 TPGOS 地址轉座標：需要 `TPGOS_GET_ADDR_XY` 設定。
3. OpenStreetMap Nominatim：使用道路/地名層級查詢。
4. 行政區中心微偏移：最後 fallback，避免點位完全消失。

輸出欄位：

- `source_row_no`
- `city`
- `normalized_city`
- `district`
- `vendor_category_code`
- `vendor_category`
- `registration_item`
- `registration_no`
- `name`
- `address`
- `company_registration_name`
- `source_page`
- `geocoding_address`
- `location_method`
- `osm_query`
- `osm_display_name`
- `taipei_house_key`：僅部分臺北市 GeoJSON 點位有此欄位，用於稽核門牌資料命中結果

前端 popup 顯示欄位：

- `name`：業者名稱
- `registration_no`：食品業者登錄字號
- `company_registration_name`：公司/商業登記名稱
- `city`：縣市
- `district`：行政區
- `address`：FDA 地址
- `vendor_category`：業者分類
- `registration_item`：登錄項目

前端 popup 已刻意隱藏的工程/追溯欄位：

- `location_method` / 定位方式
- `source_page` / 來源頁碼
- `osm_query` / OSM 查詢
- `osm_display_name`
- `taipei_house_key`

這些欄位仍保留在 GeoJSON 或 ETL 輸出中，方便後續資料稽核與定位問題排查，但不顯示在儀表板詳細資料。

### 2. 地圖 JSON 端點

```txt
POST https://fadenbook.fda.gov.tw/map/getData.ashx
```

這個端點是地圖查詢頁背後使用的資料端點，回傳 JSON，且已包含經緯度，較適合直接做 Mapbox 圖層。

常用參數：

- `keyword`：關鍵字，可留空
- `city`：縣市名稱，地圖端點臺北市建議使用 `台北市`
- `area`：行政區，例如 `中正區`、`板橋區`
- `street`：路名或地址關鍵字，可留空
- `catering`：是否查餐飲場所，例如 `true`
- `sales`：是否查販售場所，例如 `true`
- `zoom`：地圖 zoom，例如 `17`
- `isdrag`：是否使用拖曳中心點，例如 `N`
- `centerlat`：中心緯度，不使用時可填 `0`
- `centerlng`：中心經度，不使用時可填 `0`
- `cbExcellent`：是否包含「優」商家，例如 `true`
- `cbGood`：是否包含「良」商家，例如 `true`
- `cbNormal`：是否包含其他商家，例如 `true`
- `ServiceType`：餐飲業態，可留空

範例：

```txt
POST https://fadenbook.fda.gov.tw/map/getData.ashx

keyword=
city=台北市
area=中正區
street=
catering=true
sales=true
zoom=17
isdrag=N
centerlat=0
centerlng=0
cbExcellent=true
cbGood=true
cbNormal=true
ServiceType=
```

回傳欄位範例：

```json
{
  "緯度": 25.013853,
  "經度": 121.534736,
  "登錄字號": "A-188285023-00001-5",
  "公司名稱": "臨茶商行",
  "市招名稱": "台北公館店",
  "地址": "台北市中正區羅斯福路4段90巷2之1號",
  "類別": "餐飲場所",
  "評鑑": "優"
}
```

## 地圖標註建議

- 若目標是快速在地圖上標食品業者，優先使用 `map/getData.ashx`，因為它已提供經緯度。
- 建議依行政區分批抓取，例如臺北市 12 區、新北市 29 區。
- 食品業者筆數很多，不建議一次把全部點位直接畫在地圖上。
- 較適合的呈現方式：
  - 低 zoom 顯示行政區聚合數量或熱區。
  - 高 zoom 才顯示單一業者點位。
  - 或先只顯示餐飲場所、販售場所、優良商家等篩選後資料。

## 注意事項

- `search-Vendor-County-result.aspx?req=getlist` 使用 `臺北市` 可以取得列表資料。
- `map/getData.ashx` 查臺北市時，使用 `台北市` 取得的地圖資料較完整；使用 `臺北市` 會明顯少很多。
- 目前物流業圖層沒有使用 `map/getData.ashx`，因為實測地圖端點對物流業名稱常回傳 `NO`，物流業資料以縣市列表端點為準。
- 地圖端點可能有查詢上限或依地圖範圍回傳資料的行為，需要用行政區分批測試後再正式 ETL。
- 若資料要進專案的 `食安健康` tab，建議新增獨立圖層，例如：
  - `food_safety_vendor_tpe`
  - `food_safety_vendor_ntpe`
- Popup 可顯示：公司名稱、市招名稱、地址、類別、評鑑、登錄字號。
