-- Adds the health audit violation component backed by Taipei and New Taipei sanitation audit map data.

BEGIN;

INSERT INTO component_charts (index, color, types, unit)
VALUES
('health_audit_violation', '{#D84C73,#C2573E,#F5B041,#8E63C7,#4A90E2,#30B68F,#7A8793,#2F7D6D,#F2C94C,#1E88E5,#00A6A6,#AF4137}', '{DistrictChart,TreemapChart,BarChart}', '件')
ON CONFLICT (index) DO UPDATE
SET color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

INSERT INTO component_maps (id, index, title, type, source, size, icon, paint, property)
VALUES
(213, 'health_audit_violation_tpe', '臺北市衛生稽核違規單位', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#D84C73","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","violation_count"]],1],1,6,3,8,6,11],"circle-opacity":0.78,"circle-stroke-color":"#FFF2F6","circle-stroke-width":1.2}', '[{"key":"name","name":"業者名稱"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"audit_date","name":"稽查日期"},{"key":"business_category","name":"業者類別"},{"key":"inspection_result","name":"稽查結果"},{"key":"violation_reason","name":"違規說明"},{"key":"phone","name":"電話"}]'),
(214, 'health_audit_violation_ntpe', '新北市衛生稽核違規單位', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#C2573E","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","violation_count"]],1],1,6,3,8,6,11],"circle-opacity":0.78,"circle-stroke-color":"#FFF1EC","circle-stroke-width":1.2}', '[{"key":"name","name":"業者名稱"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"audit_date","name":"稽查日期"},{"key":"business_category","name":"業者主業別"},{"key":"inspection_result","name":"稽查結果"},{"key":"violation_reason","name":"違規說明"}]')
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
VALUES (309, 'health_audit_violation', '衛生稽核違規單位')
ON CONFLICT (id) DO UPDATE
SET index = EXCLUDED.index,
    name = EXCLUDED.name;

UPDATE dashboards
SET components = CASE
    WHEN components @> ARRAY[309] THEN components
    ELSE array_prepend(309, components)
END
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');

DELETE FROM query_charts
WHERE index = 'health_audit_violation';

INSERT INTO query_charts (
    index, history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart,
    query_history, city
)
VALUES
('health_audit_violation', NULL, '{213,214}', '{"mode":"byParam","byParam":{"xParam":"district"},"districtChart":{"scale":"byCity","minDataOpacity":0.22}}', 'static', NULL, NULL, NULL, '臺北市政府衛生局、新北市政府衛生局', '顯示雙北衛生稽核違規單位行政區分布。', '顯示臺北市政府衛生局食藥粧網路地圖食品業者稽查中限期改善與複查不合格單位，以及新北市食品藥物安全及衛生管理地圖「環境衛生查核」中複查不合格單位的空間分布，並以行政區圖、矩形圖與橫向長條圖呈現各行政區違規件數。data.gov.tw「臺北市食品衛生管理工作」為年度統計資料，無單位座標，作為來源背景參照而不混入地圖點位。', '可用於掌握衛生稽核需改善熱點、安排複查優先順序，並和市場、食物來源、食品物流與食品抽驗違規資料套疊分析。', '{https://fsmc.ntpc.gov.tw/DigitalMap/PublicWebsite,https://data.gov.tw/dataset/131026,https://imap.health.gov.taipei/Index.aspx,https://foodtracer.health.ntpc.gov.tw/w/foodtracer/FoodMap}', '{doit,ntpc}', NOW(), NOW(), 'two_d', 'SELECT x_axis, SUM(data)::int AS data FROM (SELECT district AS x_axis, COUNT(*)::int AS data FROM public.health_audit_violation_tpe WHERE district != '''' GROUP BY district UNION ALL SELECT district AS x_axis, COUNT(*)::int AS data FROM public.health_audit_violation_ntpe WHERE district != '''' GROUP BY district) d GROUP BY x_axis ORDER BY data DESC', NULL, 'metrotaipei'),
('health_audit_violation', NULL, '{213}', '{"mode":"byParam","byParam":{"xParam":"district"}}', 'static', NULL, NULL, NULL, '臺北市政府衛生局', '顯示臺北市衛生稽核違規單位行政區分布。', '顯示臺北市政府衛生局食藥粧網路地圖食品業者稽查中限期改善與複查不合格單位的空間分布，並以行政區圖、矩形圖與橫向長條圖呈現各行政區違規件數。資料包含業者名稱、地址、稽查日期、稽查結果與電話。', '可用於掌握臺北市衛生稽核需改善熱點、安排複查優先順序，並與食品抽驗違規資料套疊分析。', '{https://imap.health.gov.taipei/Index.aspx,https://data.gov.tw/dataset/131026}', '{doit}', NOW(), NOW(), 'two_d', 'SELECT district AS x_axis, COUNT(*)::int AS data FROM public.health_audit_violation_tpe WHERE district != '''' GROUP BY district ORDER BY data DESC', NULL, 'taipei');

SELECT setval('component_maps_id_seq', (SELECT COALESCE(MAX(id), 0) FROM component_maps), true);

COMMIT;
