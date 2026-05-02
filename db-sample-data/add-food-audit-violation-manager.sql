-- Adds the food audit violation component backed by Taipei and New Taipei food sampling data.

BEGIN;

INSERT INTO component_charts (index, color, types, unit)
VALUES
('food_audit_violation', '{#F59E0B,#D97706,#FBBF24,#EA580C,#92400E,#FDE68A,#B45309,#FDBA74}', '{DistrictChart,TreemapChart,BarChart}', '件')
ON CONFLICT (index) DO UPDATE
SET color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

INSERT INTO component_maps (id, index, title, type, source, size, icon, paint, property)
VALUES
(211, 'food_audit_violation_tpe', '臺北市食品稽核違規單位', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#F59E0B","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","violation_count"]],1],1,6,3,8,6,11],"circle-opacity":0.78,"circle-stroke-color":"#FFF7ED","circle-stroke-width":1.4}', '[{"key":"name","name":"業者名稱"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"sample_date","name":"抽驗日期"},{"key":"project_name","name":"專案名稱"},{"key":"product_category","name":"分類"},{"key":"sample_item","name":"檢體/檢驗項目"},{"key":"inspection_result","name":"檢驗結果"},{"key":"violation_reason","name":"不符合規定原因"}]'),
(212, 'food_audit_violation_ntpe', '新北市食品稽核違規單位', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#D97706","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","violation_count"]],1],1,6,3,8,6,11],"circle-opacity":0.78,"circle-stroke-color":"#FFF7ED","circle-stroke-width":1.4}', '[{"key":"name","name":"業者名稱"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"sample_date","name":"抽驗日期"},{"key":"project_name","name":"專案名稱"},{"key":"sample_item","name":"檢驗項目"},{"key":"inspection_result","name":"抽驗結果"},{"key":"violation_reason","name":"違規說明"}]')
ON CONFLICT (id) DO UPDATE
SET index = EXCLUDED.index,
    title = EXCLUDED.title,
    type = EXCLUDED.type,
    source = EXCLUDED.source,
    size = EXCLUDED.size,
    icon = EXCLUDED.icon,
    paint = EXCLUDED.paint,
    property = EXCLUDED.property;

INSERT INTO components (id, index, name)
VALUES (308, 'food_audit_violation', '食品稽核違規單位')
ON CONFLICT (id) DO UPDATE
SET index = EXCLUDED.index,
    name = EXCLUDED.name;

UPDATE dashboards
SET components = CASE
    WHEN components @> ARRAY[308] THEN components
    ELSE array_prepend(308, components)
END
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');

DELETE FROM query_charts
WHERE index = 'food_audit_violation';

INSERT INTO query_charts (
    index, history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart,
    query_history, city
)
VALUES
('food_audit_violation', NULL, '{211,212}', '{"mode":"byParam","byParam":{"xParam":"district"}}', 'static', NULL, NULL, NULL, '臺北市政府衛生局、新北市政府衛生局', '顯示雙北食品抽驗不合格單位行政區分布。', '顯示臺北市衛生局食品抽驗不合格清冊與新北市食品查驗地圖中食品抽驗不合格單位的空間分布，並以行政區圖、矩形圖與橫向長條圖呈現各行政區違規件數。資料包含業者名稱、地址、抽驗日期、檢體或檢驗項目、檢驗結果與不符合規定原因；臺北市資料以門牌資料與地址定位，新北市資料使用來源網站座標。', '可用於掌握食品抽驗違規熱點、安排衛生稽查複查與市場或物流節點套疊分析，協助食安風險溝通與稽查資源配置。', '{https://data.taipei/dataset/detail?id=09a917a0-0fb5-47e1-957c-5f1268fba517,https://fsmc.ntpc.gov.tw/DigitalMap/PublicWebsite,https://foodtracer.health.ntpc.gov.tw/w/foodtracer/FoodMap}', '{doit,ntpc}', NOW(), NOW(), 'two_d', 'SELECT x_axis, SUM(data)::int AS data FROM (SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_audit_violation_tpe WHERE district != '''' GROUP BY district UNION ALL SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_audit_violation_ntpe WHERE district != '''' GROUP BY district) d GROUP BY x_axis ORDER BY data DESC', NULL, 'metrotaipei'),
('food_audit_violation', NULL, '{211}', '{"mode":"byParam","byParam":{"xParam":"district"}}', 'static', NULL, NULL, NULL, '臺北市政府衛生局', '顯示臺北市食品抽驗不合格單位行政區分布。', '顯示臺北市衛生局食品抽驗不合格清冊的空間分布，並以行政區圖、矩形圖與橫向長條圖呈現各行政區違規件數。資料包含業者名稱、地址、抽驗日期、專案名稱、分類、檢體名稱、檢驗結果與不符合規定原因；地圖點位以門牌資料與地址定位，無法精準定位者以行政區中心點加微小偏移顯示。', '可用於掌握臺北市食品抽驗違規熱點、安排衛生稽查複查，並與市場、物流與食物來源節點套疊分析。', '{https://data.taipei/dataset/detail?id=09a917a0-0fb5-47e1-957c-5f1268fba517}', '{doit}', NOW(), NOW(), 'two_d', 'SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_audit_violation_tpe WHERE district != '''' GROUP BY district ORDER BY data DESC', NULL, 'taipei');

COMMIT;
