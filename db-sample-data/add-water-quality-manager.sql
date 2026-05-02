BEGIN;

INSERT INTO public.component_charts (index, color, types, unit) VALUES
('water_quality', '{#2F7D6D,#30B68F,#1E88E5,#F5B041,#D84C73}', '{BarChart}', 'NTU')
ON CONFLICT (index) DO UPDATE SET
  color = EXCLUDED.color,
  types = EXCLUDED.types,
  unit = EXCLUDED.unit;

INSERT INTO public.component_maps (id, index, title, type, source, size, icon, paint, property) VALUES
(207, 'water_quality_tpe', '臺北市淨水場水質', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#1E88E5","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","turbidity_ntu"]],0],0,7,0.5,9,1,12],"circle-opacity":0.78,"circle-stroke-color":"#EAF6FF","circle-stroke-width":1.4}', '[{"key":"name","name":"淨水場"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"water_sources","name":"水源"},{"key":"data_time","name":"資料時間"},{"key":"qualified","name":"合格狀態"},{"key":"ph","name":"pH值"},{"key":"turbidity_ntu","name":"濁度(NTU)"},{"key":"free_residual_chlorine_mg_l","name":"自由有效餘氯(mg/L)"},{"key":"total_hardness_mg_l","name":"總硬度(mg/L)"},{"key":"total_dissolved_solids_mg_l","name":"總溶解固體量(mg/L)"},{"key":"coliform_cfu_100ml","name":"大腸桿菌群(CFU/100mL)"}]'),
(208, 'water_quality_ntpe', '新北市淨水場水質', 'circle', 'geojson', 'big', NULL, '{"circle-color":"#00A6A6","circle-radius":["interpolate",["linear"],["coalesce",["to-number",["get","turbidity_ntu"]],0],0,7,0.5,9,1,12],"circle-opacity":0.78,"circle-stroke-color":"#E8FFFF","circle-stroke-width":1.4}', '[{"key":"name","name":"淨水場"},{"key":"english_name","name":"英文名稱"},{"key":"city","name":"縣市"},{"key":"district","name":"行政區"},{"key":"address","name":"地址"},{"key":"data_time","name":"資料時間"},{"key":"qualified","name":"合格狀態"},{"key":"ph","name":"pH值"},{"key":"turbidity_ntu","name":"濁度(NTU)"},{"key":"free_residual_chlorine_mg_l","name":"自由有效餘氯(mg/L)"},{"key":"total_hardness_mg_l","name":"總硬度(mg/L)"},{"key":"total_dissolved_solids_mg_l","name":"總溶解固體量(mg/L)"},{"key":"coliform_cfu_100ml","name":"大腸桿菌群(CFU/100mL)"}]')
ON CONFLICT (id) DO UPDATE SET
  index = EXCLUDED.index,
  title = EXCLUDED.title,
  type = EXCLUDED.type,
  source = EXCLUDED.source,
  size = EXCLUDED.size,
  icon = EXCLUDED.icon,
  paint = EXCLUDED.paint,
  property = EXCLUDED.property;

INSERT INTO public.components (id, index, name) VALUES
(306, 'water_quality', '淨水場水質')
ON CONFLICT (index) DO UPDATE SET
  name = EXCLUDED.name;

UPDATE public.components
SET id = 306
WHERE index = 'water_quality'
  AND id <> 306
  AND NOT EXISTS (SELECT 1 FROM public.components WHERE id = 306);

UPDATE public.dashboards
SET components = CASE
    WHEN components @> ARRAY[306]::integer[] THEN components
    ELSE components || 306
  END,
  updated_at = NOW()
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');

DELETE FROM public.query_charts
WHERE index = 'water_quality'
  AND city IN ('taipei', 'metrotaipei');

INSERT INTO public.query_charts (
  index, history_config, map_config_ids, map_filter, time_from, time_to,
  update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
  links, contributors, created_at, updated_at, query_type, query_chart,
  query_history, city
) VALUES
('water_quality', NULL, '{207,208}', '{}', 'static', NULL, NULL, NULL, '臺北市政府主計處、臺灣自來水股份有限公司', '顯示雙北淨水場濁度比較。', '顯示臺北自來水淨水場清水水質年度統計，以及臺灣自來水公司平均水質中關鍵字為新北市的淨水場最新測值；總覽以橫向長條圖比較各淨水場濁度(NTU)，並在地圖點位中提供 pH、濁度、自由有效餘氯、總硬度、總溶解固體量與大腸桿菌群等欄位。', '可用於掌握飲用水供應節點水質狀態，與市場、食品物流、衛生服務據點套疊，支援食安健康監測、跨區供水風險盤點與公共衛生應變。', '{https://data.taipei/dataset/detail?id=9626c65d-8fe7-45bb-bbe2-7439bed81010,https://www.water.gov.tw/ch/WaterQuality?nodeId=4631}', '{doit,ntpc}', NOW(), NOW(), 'two_d', 'SELECT unnest(array[''林莊淨水場'',''員山淨水場'',''雙溪淨水場'',''老梅淨水場'',''貢寮淨水場'',''陽明淨水場'',''坪林淨水場'',''板新淨水場'',''長興淨水場'',''公館淨水場'',''直潭淨水場'']) as x_axis, unnest(array[0.55,0.5,0.48,0.45,0.4,0.32,0.25,0.2,0.2,0.1,0.1]) as data', NULL, 'metrotaipei'),
('water_quality', NULL, '{207}', '{}', 'static', NULL, NULL, NULL, '臺北市政府主計處', '顯示臺北市淨水場濁度比較。', '顯示臺北自來水淨水場清水水質年度統計；總覽以橫向長條圖比較各淨水場濁度(NTU)，並在地圖點位中提供 pH、濁度、自由有效餘氯、總硬度、總溶解固體量與大腸桿菌群等欄位。', '可用於掌握臺北飲用水供應節點水質狀態，與市場、食品物流、衛生服務據點套疊，支援食安健康監測與公共衛生應變。', '{https://data.taipei/dataset/detail?id=9626c65d-8fe7-45bb-bbe2-7439bed81010}', '{doit}', NOW(), NOW(), 'two_d', 'SELECT unnest(array[''雙溪淨水場'',''陽明淨水場'',''長興淨水場'',''公館淨水場'',''直潭淨水場'']) as x_axis, unnest(array[0.48,0.32,0.2,0.1,0.1]) as data', NULL, 'taipei');

SELECT setval('public.components_id_seq', (SELECT COALESCE(MAX(id), 0) FROM public.components), true);
SELECT setval('public.component_maps_id_seq', (SELECT COALESCE(MAX(id), 0) FROM public.component_maps), true);

COMMIT;
