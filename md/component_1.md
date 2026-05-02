# 組件1：食品廠商 FDA 食品業者登錄 API 筆記

最後更新：2026-05-02

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

範例：

```txt
https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?req=getlist&city=臺北市&Page=1&Size=40&tp=0
```

目前觀察：

- 臺北市列表頁顯示約 98,216 筆。
- 這個端點資料較完整，但沒有直接提供經緯度。
- 若要拿來上地圖，需要再用地址做地理編碼。

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
- 地圖端點可能有查詢上限或依地圖範圍回傳資料的行為，需要用行政區分批測試後再正式 ETL。
- 若資料要進專案的 `食安健康` tab，建議新增獨立圖層，例如：
  - `food_safety_vendor_tpe`
  - `food_safety_vendor_ntpe`
- Popup 可顯示：公司名稱、市招名稱、地址、類別、評鑑、登錄字號。
