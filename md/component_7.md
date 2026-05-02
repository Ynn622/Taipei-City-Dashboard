# 組件7：衛生稽核違規單位

## Dashboard

- Component：`309 / health_audit_violation / 衛生稽核違規單位`
- Charts：`DistrictChart`、`TreemapChart`、`BarChart`
- Unit：`件`
- Maps：
  - `213 / health_audit_violation_tpe / 臺北市衛生稽核違規單位`
  - `214 / health_audit_violation_ntpe / 新北市衛生稽核違規單位`
- Dashboards：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`

## 資料處理

- 臺北市：使用 `https://imap.health.gov.taipei/Index.aspx` 的地圖搜尋，條件為「食品 / 全站搜尋 / 限期改善、複查不合格」。回傳資料含業者名稱、地址、座標、電話、稽查日期與稽查結果。
- 新北市：使用 `https://fsmc.ntpc.gov.tw/DigitalMap/PublicWebsite` 的「環境衛生查核」API `GetFilteredGHPStoresWithCoordinates`，保留 `稽查結果 = 複查不合格`。
- `https://data.gov.tw/dataset/131026` 是臺北市食品衛生管理工作年度統計，沒有違規單位地址或座標，因此納入來源說明，不混入點位資料。
- `https://foodtracer.health.ntpc.gov.tw/w/foodtracer/FoodMap` 與新北市食安地圖同屬衛生查核/食安參考來源；本組件點位以可穩定取得的 GHP API 為準。

## Files

- 臺北市 DAG：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/health_audit_violation_tpe/`
- 新北市 DAG：`Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/health_audit_violation_ntpe/`
- Manager SQL：`db-sample-data/add-health-audit-violation-manager.sql`
- Frontend map data：
  - `Taipei-City-Dashboard-FE/public/mapData/health_audit_violation_tpe.geojson`
  - `Taipei-City-Dashboard-FE/public/mapData/health_audit_violation_ntpe.geojson`
