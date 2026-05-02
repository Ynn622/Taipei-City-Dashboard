# 組件10：事後求助機構

## Dashboard 設定

- Component：`310 / post_help_agency / 事後求助機構`
- Chart：`TreemapChart`、`BarChart`
- Chart 維度：`agency_type`
  - `藥局`
  - `西醫一般科`
  - `內科`
  - `家庭醫學科`
  - `急診醫學科`
  - `消保會`
  - `消費者服務中心`
  - `消基會`
  - 同一機構跨多個科別時，會以 `、` 合併為複合類型。
- Map layers：
  - `215 / post_help_agency_tpe / 臺北市事後求助機構`
  - `216 / post_help_agency_ntpe / 新北市事後求助機構`
- 地圖標點：
  - 藥局：綠色
  - 西醫一般科：藍色
  - 內科：青色
  - 家庭醫學科：紫色
  - 急診醫學科：紅色
  - 複合科別：橘色
  - 民間保護機構：玫紅色
  - 點位大小依 `specialty_count` 微幅放大，同一醫院跨越多個科別時較容易辨識。

## 資料來源

### 醫療機構

- 新北市非健保特約藥局名單
- 新北市健保特約藥局名單
- 新北市西醫一般科醫療機構
- 新北市內科醫療機構
- 新北市家庭醫學科醫療機構
- 新北市急診學學科醫療機構
- 臺北市藥局
- 臺北市西醫一般科醫療機構
- 臺北市內科醫療機構
- 臺北市家庭醫學科醫療機構
- 臺北市急診醫學科醫療機構

### 民間保護機構

- 消保會：臺北市中正區北平東路2號
- 臺北市消費者服務中心：臺北市信義區市府路1號8樓
- 新北市消費者服務中心：新北市板橋區中山路1段161號1樓聯合服務中心
- 消基會：臺北市大安區復興南路1段390號10樓之3

## ETL 策略

- 醫療資料以「縣市 + 名稱 + 地址」去重。
- 不同科別出現同一醫院時，保留單一點位，並將科別合併到 `specialties`，同時計算 `specialty_count`。
- 臺北市藥局使用來源座標；其他臺北醫療機構優先用臺北市門牌位置數值資料定位，缺值以行政區中心微偏移補點。
- 新北市資料優先使用來源 API 的 WGS84 座標，缺值以行政區中心微偏移補點。
- 詳細資訊不顯示 `location_method`，避免把定位技術欄位露出給使用者。

## 本機 demo 狀態

- 臺北市：`1946` 筆，依 `agency_type` 分類：
  - 藥局：`907`
  - 西醫一般科：`641`
  - 內科：`180`
  - 家庭醫學科：`151`
  - 急診醫學科：`15`
  - 其他單一或複合類型：`52`
- 新北市：`2136` 筆，依 `agency_type` 分類：
  - 藥局：`1282`
  - 西醫一般科：`423`
  - 家庭醫學科：`203`
  - 內科：`174`
  - 其他單一或複合類型：`54`
- 雙北合計前五大：
  - 藥局：`2189`
  - 西醫一般科：`1064`
  - 內科：`354`
  - 家庭醫學科：`354`
  - 內科、家庭醫學科：`68`

## 相關檔案

- 臺北市 DAG：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/post_help_agency_tpe/`
- 新北市 DAG：`Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/post_help_agency_ntpe/`
- 共用整理邏輯：`Taipei-City-Dashboard-DE/dags/utils/post_help_agency.py`
- Manager SQL：`db-sample-data/add-post-help-agency-manager.sql`
- GeoJSON：
  - `Taipei-City-Dashboard-FE/public/mapData/post_help_agency_tpe.geojson`
  - `Taipei-City-Dashboard-FE/public/mapData/post_help_agency_ntpe.geojson`
