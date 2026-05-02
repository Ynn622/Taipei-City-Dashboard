-- Adds the food source component backed by Taipei and New Taipei organic farm APIs.

BEGIN;

INSERT INTO component_charts (index, color, types, unit)
VALUES
('food_source', '{#30B68F,#F5B041,#4A90E2,#D84C73,#8E63C7,#F2C94C,#7A8793,#2F7D6D,#C2573E,#1E88E5,#00A6A6,#AF4137}', '{DistrictChart,TreemapChart,BarChart}', '處')
ON CONFLICT (index) DO UPDATE
SET color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

INSERT INTO component_maps (id, index, title, type, source, size, icon, paint, property)
VALUES
(209, 'food_source_tpe', '臺北市有機農場', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#30B68F","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","area_ha"]],0.1],0,5,0.5,7,1,9,2,12,5,16],"circle-opacity":0.74,"circle-stroke-color":"#F7FFF9","circle-stroke-width":1}', '[{"key":"name","name":"農場名稱"},{"key":"operator","name":"農友/經營者"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"certification_no","name":"認證字號"},{"key":"certification_status","name":"驗證狀態"},{"key":"area_ha","name":"面積(公頃)"},{"key":"food_education","name":"食農教育體驗"},{"key":"beekeeping","name":"飼養蜜蜂"},{"key":"chicken_raising","name":"飼養雞隻"},{"key":"location_method","name":"定位方式"}]'),
(210, 'food_source_ntpe', '新北市有機農場', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#F5B041","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","area_ha"]],0.1],0,5,0.5,7,1,9,2,12,5,16],"circle-opacity":0.74,"circle-stroke-color":"#FFF8E8","circle-stroke-width":1}', '[{"key":"name","name":"農場名稱"},{"key":"operator","name":"農友/經營者"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"phone","name":"電話"},{"key":"certification_valid_until","name":"有效日期"},{"key":"certification_status","name":"驗證狀態"},{"key":"area_ha","name":"面積(公頃)"},{"key":"location_method","name":"定位方式"}]')
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
VALUES (307, 'food_source', '食物來源')
ON CONFLICT (id) DO UPDATE
SET index = EXCLUDED.index,
    name = EXCLUDED.name;

UPDATE dashboards
SET components = CASE
    WHEN components @> ARRAY[307] THEN components
    ELSE array_prepend(307, components)
END
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');

DELETE FROM query_charts
WHERE index = 'food_source';

INSERT INTO query_charts (
    index, history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart,
    query_history, city
)
VALUES
('food_source', NULL, '{209,210}', '{"mode":"byParam","byParam":{"xParam":"district"}}', 'static', NULL, NULL, NULL, '臺北市政府產業發展局、新北市政府農業局', '顯示雙北有機農場來源分布。', '顯示臺北市取得有機驗證之有機農場與新北市有機農場之空間分布，並以行政區圖、矩形圖與橫向長條圖呈現各行政區有機農場數量。資料包含農場名稱、經營者、行政區、地址、驗證狀態、面積與聯絡資訊；地址可定位者使用地址座標，地號或無法定位者以行政區中心點加微小偏移顯示，作為食物來源與食安供應鏈節點盤點基礎。', '可用於掌握雙北有機農產品來源分布、食安供應鏈來源追蹤、產地與市場或物流節點套疊分析，以及農業資源與稽查服務配置。', '{https://data.taipei/dataset/detail?id=32aea2da-14a7-47b6-a687-57e29c1ad4a7,https://data.ntpc.gov.tw/datasets/fc30f585-66d9-4233-a65e-c650d177ebfe}', '{doit,ntpc}', NOW(), NOW(), 'two_d', 'SELECT x_axis, SUM(data)::int AS data FROM (SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_source_tpe WHERE district != '''' GROUP BY district UNION ALL SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_source_ntpe WHERE district != '''' GROUP BY district) d GROUP BY x_axis ORDER BY data DESC', NULL, 'metrotaipei'),
('food_source', NULL, '{209}', '{"mode":"byParam","byParam":{"xParam":"district"}}', 'static', NULL, NULL, NULL, '臺北市政府產業發展局', '顯示臺北市有機農場來源分布。', '顯示臺北市取得有機驗證之有機農場空間分布，並以行政區圖、矩形圖與橫向長條圖呈現各行政區有機農場數量。資料包含農場名稱、農友姓名、行政區、地址、認證字號、面積與食農教育等欄位；地址可定位者使用地址座標，無法定位者以行政區中心點加微小偏移顯示，作為食物來源與食安供應鏈節點盤點基礎。', '可用於掌握臺北市有機農產品來源分布、食安供應鏈來源追蹤、產地與市場或物流節點套疊分析，以及農業資源與稽查服務配置。', '{https://data.taipei/dataset/detail?id=32aea2da-14a7-47b6-a687-57e29c1ad4a7}', '{doit}', NOW(), NOW(), 'two_d', 'SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_source_tpe WHERE district != '''' GROUP BY district ORDER BY data DESC', NULL, 'taipei');

COMMIT;
