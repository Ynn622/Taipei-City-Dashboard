# 組件8：食品稽核違規單位

## 資料來源

- 臺北市：臺北市衛生局食品抽驗不合格清冊
  - https://data.taipei/dataset/detail?id=09a917a0-0fb5-47e1-957c-5f1268fba517
- 新北市：食品查驗地圖 / 食品抽驗結果
  - https://fsmc.ntpc.gov.tw/DigitalMap/PublicWebsite
  - https://foodtracer.health.ntpc.gov.tw/w/foodtracer/FoodMap

## 儀表板設定

- Component：`308 / food_audit_violation / 食品稽核違規單位`
- Map config：
  - `211 / food_audit_violation_tpe / 臺北市食品稽核違規單位`
  - `212 / food_audit_violation_ntpe / 新北市食品稽核違規單位`
- Chart：`DistrictChart`、`TreemapChart`、`BarChart`
- 單位：`件`

## 欄位

- `name`：業者名稱
- `city`：縣市
- `district`：行政區
- `address`：地址
- `sample_date`：抽驗日期
- `project_name`：專案名稱
- `product_category`：分類
- `sample_item`：檢體或檢驗項目
- `inspection_result`：檢驗結果
- `violation_reason`：不符合規定原因或違規說明

## ETL

- 臺北市 DAG：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_audit_violation_tpe/food_audit_violation_tpe.py`
- 新北市 DAG：`Taipei-City-Dashboard-DE/dags/proj_new_taipei_city_dashboard/food_audit_violation_ntpe/food_audit_violation_ntpe.py`

臺北市資料來源為 data.taipei CSV resources，ETL 會從資料集頁面探索可下載的 resource，整併各年度不合格清冊並以門牌資料與 OpenStreetMap 輔助定位。新北市資料來源為食品查驗地圖背後的全區食品抽驗結果端點，ETL 保留抽驗結果為不合格的紀錄並使用來源網站提供的座標。
