# 組件14：食品加工抽驗不合格率

最後更新：2026-05-03

## 基本設定

- Dashboard 名稱：食安健康
- Dashboard index：
  - `food_safety_health_tpe`
  - `food_safety_health_metrotaipei`
- Component index：`food_processing_pass_rate`
- Component id：`505`
- Component 名稱：食品加工抽驗不合格率
- 圖表類型：`TimelineSeparateChart`
- 單位：`%`
- Query type：`time`
- Map config：無

## 指標口徑

此 component 彙整衛生福利部食品衛生管理工作資料，篩選肉品、蛋品、水產、蔬果及食品添加物五大類，計算各年度不合格率並以折線圖呈現趨勢。

目前 query 使用：

```text
non_compliant_count / inspection_count * 100
```

## 資料範圍

- 年度：民國 105 至 114 年
- 城市：臺北市、新北市
- 類別：
  - 肉品類
  - 蛋品類
  - 水產類
  - 蔬果類
  - 添加物

## 資料表

- `public.food_processing_pass_rate`

主要欄位：

- `year`
- `county`
- `category`
- `inspection_count`
- `non_compliant_count`
- `pass_rate`

## ETL DAG

- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_processing_pass_rate/food_processing_pass_rate.py`
- `Taipei-City-Dashboard-DE/dags/proj_city_dashboard/food_processing_pass_rate/job_config.json`

## Seed SQL

- `db-sample-data/add-food-processing-pass-rate.sql`
- `db-sample-data/food-processing-pass-rate-data.sql`

## 注意事項

- Manager component 名稱可呈現為合格率或不合格率，但 SQL query 目前輸出的是不合格率。
- 若要改顯示合格率，需同步調整 query、圖表文字與文件命名。
