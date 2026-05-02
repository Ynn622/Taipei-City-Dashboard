-- Adds component 10: post-incident help agencies backed by medical institution
-- open data and fixed consumer protection agency locations.

BEGIN;

INSERT INTO component_charts (index, color, types, unit)
VALUES
('post_help_agency', '{#16A34A,#2563EB,#0891B2,#7C3AED,#F59E0B,#DC2626,#E11D48,#475569,#65A30D,#DB2777,#9333EA,#EA580C,#0284C7,#7C2D12,#4B5563}', '{TreemapChart,BarChart}', '處')
ON CONFLICT (index) DO UPDATE
SET color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

INSERT INTO component_maps (id, index, title, type, source, size, icon, paint, property)
VALUES
(215, 'post_help_agency_tpe', '臺北市事後求助機構', 'circle', 'geojson', 'big', NULL, '{"circle-color":["match",["get","agency_type"],"藥局","#16A34A","西醫一般科","#2563EB","內科","#0891B2","家庭醫學科","#7C3AED","急診醫學科","#DC2626",["消保會","消費者服務中心","消基會"],"#E11D48",["內科、家庭醫學科","西醫一般科、內科、家庭醫學科","西醫一般科、內科、家庭醫學科、急診醫學科","西醫一般科、家庭醫學科","內科、家庭醫學科、急診醫學科","西醫一般科、內科","家庭醫學科、急診醫學科","內科、急診醫學科"],"#F59E0B","#64748B"],"circle-radius":["interpolate",["linear"],["zoom"],9,3,12,4,15,6],"circle-opacity":0.78,"circle-stroke-color":["match",["get","agency_type"],"藥局","#DCFCE7","西醫一般科","#DBEAFE","內科","#CFFAFE","家庭醫學科","#EDE9FE","急診醫學科","#FEE2E2",["消保會","消費者服務中心","消基會"],"#FFE4E6",["內科、家庭醫學科","西醫一般科、內科、家庭醫學科","西醫一般科、內科、家庭醫學科、急診醫學科","西醫一般科、家庭醫學科","內科、家庭醫學科、急診醫學科","西醫一般科、內科","家庭醫學科、急診醫學科","內科、急診醫學科"],"#FEF3C7","#E2E8F0"],"circle-stroke-width":1.2}', '[{"key":"name","name":"名稱"},{"key":"agency_group","name":"大類"},{"key":"agency_type","name":"類型"},{"key":"specialties","name":"科別/服務"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"phone","name":"電話"},{"key":"is_nhi_contracted","name":"健保特約"}]'),
(216, 'post_help_agency_ntpe', '新北市事後求助機構', 'circle', 'geojson', 'big', NULL, '{"circle-color":["match",["get","agency_type"],"藥局","#16A34A","西醫一般科","#2563EB","內科","#0891B2","家庭醫學科","#7C3AED","急診醫學科","#DC2626",["消保會","消費者服務中心","消基會"],"#E11D48",["內科、家庭醫學科","西醫一般科、內科、家庭醫學科","西醫一般科、內科、家庭醫學科、急診醫學科","西醫一般科、家庭醫學科","內科、家庭醫學科、急診醫學科","西醫一般科、內科","家庭醫學科、急診醫學科","內科、急診醫學科"],"#F59E0B","#64748B"],"circle-radius":["interpolate",["linear"],["zoom"],9,3,12,4,15,6],"circle-opacity":0.78,"circle-stroke-color":["match",["get","agency_type"],"藥局","#DCFCE7","西醫一般科","#DBEAFE","內科","#CFFAFE","家庭醫學科","#EDE9FE","急診醫學科","#FEE2E2",["消保會","消費者服務中心","消基會"],"#FFE4E6",["內科、家庭醫學科","西醫一般科、內科、家庭醫學科","西醫一般科、內科、家庭醫學科、急診醫學科","西醫一般科、家庭醫學科","內科、家庭醫學科、急診醫學科","西醫一般科、內科","家庭醫學科、急診醫學科","內科、急診醫學科"],"#FEF3C7","#E2E8F0"],"circle-stroke-width":1.2}', '[{"key":"name","name":"名稱"},{"key":"agency_group","name":"大類"},{"key":"agency_type","name":"類型"},{"key":"specialties","name":"科別/服務"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"phone","name":"電話"},{"key":"is_nhi_contracted","name":"健保特約"}]')
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
VALUES (310, 'post_help_agency', '事後求助機構')
ON CONFLICT (id) DO UPDATE
SET index = EXCLUDED.index,
    name = EXCLUDED.name;

UPDATE dashboards
SET components = CASE
    WHEN components @> ARRAY[310] THEN components
    ELSE array_prepend(310, components)
END
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');

DELETE FROM query_charts
WHERE index = 'post_help_agency';

INSERT INTO query_charts (
    index, history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart,
    query_history, city
)
VALUES
('post_help_agency', NULL, '{215,216}', '{"mode":"byParam","byParam":{"xParam":"agency_type"}}', 'static', NULL, NULL, NULL, '臺北市政府衛生局、新北市政府衛生局、行政院消費者保護處、臺北市政府法務局、新北市政府法制局、財團法人中華民國消費者文教基金會', '顯示雙北各類事後求助機構節點。', '整合臺北市與新北市藥局、西醫一般科、內科、家庭醫學科、急診醫學科醫療機構，以及消保會、消費者服務中心與消基會等事後求助節點。相同醫院若出現在不同科別資料中，會以名稱與地址去重並合併類型，地圖以單一點位呈現；圖表可依「藥局」、「西醫一般科」、「內科」、「家庭醫學科」、「急診醫學科」、「消費者服務中心」等類型切換查看。', '可用於食品安全或消費爭議事件後，快速掌握醫療處置與民間保護/申訴支援節點，並和食品稽核、衛生稽核、有機農場與市場圖資套疊分析。', '{https://staging.data.ntpc.gov.tw/datasets/f379e6dc-5a60-49a7-a47b-d3887566e157,https://staging.data.ntpc.gov.tw/datasets/fdbefc45-7005-49ab-a56d-41881e435dc2,https://staging.data.ntpc.gov.tw/datasets/ec49095f-7383-4008-ba4f-3208068ceaa8,https://staging.data.ntpc.gov.tw/datasets/e8244d31-e0e5-459d-87ba-3c188706fbee,https://staging.data.ntpc.gov.tw/datasets/9e1c1aba-4e0b-4d5a-8755-efa1f09abe65,https://staging.data.ntpc.gov.tw/datasets/7e4a9359-61dd-4a3c-9ebc-8e2b0b380a13,https://data.taipei/dataset/detail?id=6fa3ed67-e60e-44d9-a366-ce7008e322de,https://data.taipei/dataset/detail?id=dfd0f10f-0f4d-4c92-96bc-997e7596297d,https://data.taipei/dataset/detail?id=dbb54bf8-74a8-475d-ae88-a0ec4262c39a,https://data.taipei/dataset/detail?id=34e855c7-7808-46d2-b9b1-f7244fe2b9b5,https://data.taipei/dataset/detail?id=73452edf-a60f-4f47-86d0-d4295e4fa79d}', '{doit,ntpc}', NOW(), NOW(), 'two_d', 'SELECT x_axis, SUM(data)::int AS data FROM (SELECT agency_type AS x_axis, COUNT(*)::int AS data FROM public.post_help_agency_tpe WHERE agency_type != '''' GROUP BY agency_type UNION ALL SELECT agency_type AS x_axis, COUNT(*)::int AS data FROM public.post_help_agency_ntpe WHERE agency_type != '''' GROUP BY agency_type) d GROUP BY x_axis ORDER BY data DESC', NULL, 'metrotaipei'),
('post_help_agency', NULL, '{215}', '{"mode":"byParam","byParam":{"xParam":"agency_type"}}', 'static', NULL, NULL, NULL, '臺北市政府衛生局、行政院消費者保護處、臺北市政府法務局、財團法人中華民國消費者文教基金會', '顯示臺北市各類事後求助機構節點。', '整合臺北市藥局、西醫一般科、內科、家庭醫學科、急診醫學科醫療機構，以及消保會、臺北市消費者服務中心與消基會等事後求助節點。相同醫院若出現在不同科別資料中，會以名稱與地址去重並合併類型，地圖以單一點位呈現；圖表可依「藥局」、「西醫一般科」、「內科」、「家庭醫學科」、「急診醫學科」、「消保會」、「消費者服務中心」、「消基會」等類型切換查看。', '可用於食品安全或消費爭議事件後，快速掌握臺北市醫療處置與民間保護/申訴支援節點。', '{https://data.taipei/dataset/detail?id=6fa3ed67-e60e-44d9-a366-ce7008e322de,https://data.taipei/dataset/detail?id=dfd0f10f-0f4d-4c92-96bc-997e7596297d,https://data.taipei/dataset/detail?id=dbb54bf8-74a8-475d-ae88-a0ec4262c39a,https://data.taipei/dataset/detail?id=34e855c7-7808-46d2-b9b1-f7244fe2b9b5,https://data.taipei/dataset/detail?id=73452edf-a60f-4f47-86d0-d4295e4fa79d}', '{doit}', NOW(), NOW(), 'two_d', 'SELECT agency_type AS x_axis, COUNT(*)::int AS data FROM public.post_help_agency_tpe WHERE agency_type != '''' GROUP BY agency_type ORDER BY data DESC', NULL, 'taipei');

COMMIT;
