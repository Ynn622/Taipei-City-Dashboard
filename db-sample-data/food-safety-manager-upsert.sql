BEGIN;

INSERT INTO public.component_maps ("index", title, type, source, size, icon, paint, property)
SELECT
  'food_safety_market_tpe',
  '臺北市公有市場',
  'circle',
  'geojson',
  'big',
  NULL,
  '{
    "circle-color": "#30B68F",
    "circle-opacity": 0.75,
    "circle-stroke-color": "#F7FFF9",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["coalesce", ["to-number", ["get", "stall_total"]], 80], 0, 6, 100, 10, 300, 18, 600, 28]
  }'::json,
  '[
    {"key":"name","name":"市場名稱"},
    {"key":"district","name":"行政區"},
    {"key":"stall_total","name":"總攤位數"},
    {"key":"vegetable_stalls","name":"蔬菜攤位"},
    {"key":"fruit_stalls","name":"青果攤位"},
    {"key":"meat_stalls","name":"獸肉攤位"},
    {"key":"seafood_stalls","name":"漁產攤位"},
    {"key":"poultry_stalls","name":"家禽攤位"},
    {"key":"grain_stalls","name":"糧食攤位"},
    {"key":"flower_stalls","name":"花卉攤位"},
    {"key":"grocery_stalls","name":"雜貨攤位"},
    {"key":"general_merchandise_stalls","name":"百貨攤位"},
    {"key":"food_stalls","name":"飲食攤位"},
    {"key":"other_stalls","name":"其他攤位"}
  ]'::json
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_maps WHERE "index" = 'food_safety_market_tpe'
);

UPDATE public.component_maps
SET
  title = '臺北市公有市場',
  type = 'circle',
  source = 'geojson',
  size = 'big',
  icon = NULL,
  paint = '{
    "circle-color": "#30B68F",
    "circle-opacity": 0.75,
    "circle-stroke-color": "#F7FFF9",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["coalesce", ["to-number", ["get", "stall_total"]], 80], 0, 6, 100, 10, 300, 18, 600, 28]
  }'::json,
  property = '[
    {"key":"name","name":"市場名稱"},
    {"key":"district","name":"行政區"},
    {"key":"stall_total","name":"總攤位數"},
    {"key":"vegetable_stalls","name":"蔬菜攤位"},
    {"key":"fruit_stalls","name":"青果攤位"},
    {"key":"meat_stalls","name":"獸肉攤位"},
    {"key":"seafood_stalls","name":"漁產攤位"},
    {"key":"poultry_stalls","name":"家禽攤位"},
    {"key":"grain_stalls","name":"糧食攤位"},
    {"key":"flower_stalls","name":"花卉攤位"},
    {"key":"grocery_stalls","name":"雜貨攤位"},
    {"key":"general_merchandise_stalls","name":"百貨攤位"},
    {"key":"food_stalls","name":"飲食攤位"},
    {"key":"other_stalls","name":"其他攤位"}
  ]'::json
WHERE "index" = 'food_safety_market_tpe';

INSERT INTO public.component_maps ("index", title, type, source, size, icon, paint, property)
SELECT
  'food_safety_market_ntpe',
  '新北市公有市場',
  'circle',
  'geojson',
  'big',
  NULL,
  '{
    "circle-color": "#F5B041",
    "circle-opacity": 0.75,
    "circle-stroke-color": "#FFF8E8",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["coalesce", ["to-number", ["get", "stall_total"]], 80], 0, 6, 100, 10, 300, 18, 600, 28]
  }'::json,
  '[
    {"key":"name","name":"市場名稱"},
    {"key":"district","name":"行政區"},
    {"key":"stall_total","name":"總攤位數"},
    {"key":"produce_stalls","name":"果菜攤位"},
    {"key":"meat_stalls","name":"畜肉攤位"},
    {"key":"seafood_stalls","name":"魚蝦攤位"},
    {"key":"poultry_stalls","name":"禽肉攤位"},
    {"key":"grain_stalls","name":"糧食攤位"},
    {"key":"grocery_stalls","name":"雜貨攤位"},
    {"key":"flower_stalls","name":"花卉攤位"},
    {"key":"food_stalls","name":"飲食攤位"},
    {"key":"general_merchandise_stalls","name":"百貨攤位"},
    {"key":"other_stalls","name":"其他攤位"},
    {"key":"vacant_stalls","name":"空攤"},
    {"key":"address","name":"地址"},
    {"key":"phone","name":"電話"},
    {"key":"type","name":"市場型態"}
  ]'::json
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_maps WHERE "index" = 'food_safety_market_ntpe'
);

UPDATE public.component_maps
SET
  title = '新北市公有市場',
  type = 'circle',
  source = 'geojson',
  size = 'big',
  icon = NULL,
  paint = '{
    "circle-color": "#F5B041",
    "circle-opacity": 0.75,
    "circle-stroke-color": "#FFF8E8",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["coalesce", ["to-number", ["get", "stall_total"]], 80], 0, 6, 100, 10, 300, 18, 600, 28]
  }'::json,
  property = '[
    {"key":"name","name":"市場名稱"},
    {"key":"district","name":"行政區"},
    {"key":"stall_total","name":"總攤位數"},
    {"key":"produce_stalls","name":"果菜攤位"},
    {"key":"meat_stalls","name":"畜肉攤位"},
    {"key":"seafood_stalls","name":"魚蝦攤位"},
    {"key":"poultry_stalls","name":"禽肉攤位"},
    {"key":"grain_stalls","name":"糧食攤位"},
    {"key":"grocery_stalls","name":"雜貨攤位"},
    {"key":"flower_stalls","name":"花卉攤位"},
    {"key":"food_stalls","name":"飲食攤位"},
    {"key":"general_merchandise_stalls","name":"百貨攤位"},
    {"key":"other_stalls","name":"其他攤位"},
    {"key":"vacant_stalls","name":"空攤"},
    {"key":"address","name":"地址"},
    {"key":"phone","name":"電話"},
    {"key":"type","name":"市場型態"}
  ]'::json
WHERE "index" = 'food_safety_market_ntpe';

INSERT INTO public.component_maps ("index", title, type, source, size, icon, paint, property)
SELECT
  'food_safety_logistics_vendor_tpe',
  '臺北市食品物流業者',
  'circle',
  'geojson',
  'small',
  NULL,
  '{
    "circle-color": "#4F8EF7",
    "circle-opacity": 0.72,
    "circle-stroke-color": "#F5F9FF",
    "circle-stroke-width": 1,
    "circle-radius": 6
  }'::json,
  '[
    {"key":"name","name":"業者名稱"},
    {"key":"registration_no","name":"登錄字號"},
    {"key":"company_registration_name","name":"公司/商業登記名稱"},
    {"key":"city","name":"縣市"},
    {"key":"district","name":"行政區"},
    {"key":"address","name":"地址"},
    {"key":"vendor_category","name":"業者分類"},
    {"key":"registration_item","name":"登錄項目"}
  ]'::json
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_maps WHERE "index" = 'food_safety_logistics_vendor_tpe'
);

UPDATE public.component_maps
SET
  title = '臺北市食品物流業者',
  type = 'circle',
  source = 'geojson',
  size = 'small',
  icon = NULL,
  paint = '{
    "circle-color": "#4F8EF7",
    "circle-opacity": 0.72,
    "circle-stroke-color": "#F5F9FF",
    "circle-stroke-width": 1,
    "circle-radius": 6
  }'::json,
  property = '[
    {"key":"name","name":"業者名稱"},
    {"key":"registration_no","name":"登錄字號"},
    {"key":"company_registration_name","name":"公司/商業登記名稱"},
    {"key":"city","name":"縣市"},
    {"key":"district","name":"行政區"},
    {"key":"address","name":"地址"},
    {"key":"vendor_category","name":"業者分類"},
    {"key":"registration_item","name":"登錄項目"}
  ]'::json
WHERE "index" = 'food_safety_logistics_vendor_tpe';

INSERT INTO public.component_maps ("index", title, type, source, size, icon, paint, property)
SELECT
  'food_safety_logistics_vendor_ntpe',
  '新北市食品物流業者',
  'circle',
  'geojson',
  'small',
  NULL,
  '{
    "circle-color": "#7B5EF5",
    "circle-opacity": 0.72,
    "circle-stroke-color": "#F7F3FF",
    "circle-stroke-width": 1,
    "circle-radius": 6
  }'::json,
  '[
    {"key":"name","name":"業者名稱"},
    {"key":"registration_no","name":"登錄字號"},
    {"key":"company_registration_name","name":"公司/商業登記名稱"},
    {"key":"city","name":"縣市"},
    {"key":"district","name":"行政區"},
    {"key":"address","name":"地址"},
    {"key":"vendor_category","name":"業者分類"},
    {"key":"registration_item","name":"登錄項目"}
  ]'::json
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_maps WHERE "index" = 'food_safety_logistics_vendor_ntpe'
);

UPDATE public.component_maps
SET
  title = '新北市食品物流業者',
  type = 'circle',
  source = 'geojson',
  size = 'small',
  icon = NULL,
  paint = '{
    "circle-color": "#7B5EF5",
    "circle-opacity": 0.72,
    "circle-stroke-color": "#F7F3FF",
    "circle-stroke-width": 1,
    "circle-radius": 6
  }'::json,
  property = '[
    {"key":"name","name":"業者名稱"},
    {"key":"registration_no","name":"登錄字號"},
    {"key":"company_registration_name","name":"公司/商業登記名稱"},
    {"key":"city","name":"縣市"},
    {"key":"district","name":"行政區"},
    {"key":"address","name":"地址"},
    {"key":"vendor_category","name":"業者分類"},
    {"key":"registration_item","name":"登錄項目"}
  ]'::json
WHERE "index" = 'food_safety_logistics_vendor_ntpe';

INSERT INTO public.components ("index", name)
SELECT 'food_safety_market', '公有市場圖資'
WHERE NOT EXISTS (
  SELECT 1 FROM public.components WHERE "index" = 'food_safety_market'
);

UPDATE public.components
SET name = '公有市場圖資'
WHERE "index" = 'food_safety_market';

INSERT INTO public.component_charts ("index", color, types, unit)
SELECT
  'food_safety_market',
  ARRAY['#30B68F', '#F5B041'],
  ARRAY['MapLegend'],
  '處'
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_charts WHERE "index" = 'food_safety_market'
);

UPDATE public.component_charts
SET
  color = ARRAY['#30B68F', '#F5B041'],
  types = ARRAY['MapLegend'],
  unit = '處'
WHERE "index" = 'food_safety_market';

INSERT INTO public.components ("index", name)
SELECT 'food_safety_logistics_vendor', '食品物流業者'
WHERE NOT EXISTS (
  SELECT 1 FROM public.components WHERE "index" = 'food_safety_logistics_vendor'
);

UPDATE public.components
SET name = '食品物流業者'
WHERE "index" = 'food_safety_logistics_vendor';

INSERT INTO public.component_charts ("index", color, types, unit)
SELECT
  'food_safety_logistics_vendor',
  ARRAY['#4F8EF7', '#7B5EF5'],
  ARRAY['MapLegend'],
  '家'
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_charts WHERE "index" = 'food_safety_logistics_vendor'
);

UPDATE public.component_charts
SET
  color = ARRAY['#4F8EF7', '#7B5EF5'],
  types = ARRAY['MapLegend'],
  unit = '家'
WHERE "index" = 'food_safety_logistics_vendor';

DO $$
DECLARE
  v_market_component_id integer;
  v_logistics_component_id integer;
  v_fda_component_id integer;
  v_market_tpe_map_id integer;
  v_market_ntpe_map_id integer;
  v_logistics_tpe_map_id integer;
  v_logistics_ntpe_map_id integer;
  v_tpe_dashboard_id integer;
  v_metrotpe_dashboard_id integer;
  v_taipei_group_id integer;
  v_metrotaipei_group_id integer;
BEGIN
  SELECT id INTO v_market_component_id FROM public.components WHERE "index" = 'food_safety_market';
  SELECT id INTO v_logistics_component_id FROM public.components WHERE "index" = 'food_safety_logistics_vendor';
  SELECT id INTO v_fda_component_id FROM public.components WHERE "index" = 'fda_good_restaurants';

  SELECT id INTO v_market_tpe_map_id FROM public.component_maps WHERE "index" = 'food_safety_market_tpe';
  SELECT id INTO v_market_ntpe_map_id FROM public.component_maps WHERE "index" = 'food_safety_market_ntpe';
  SELECT id INTO v_logistics_tpe_map_id FROM public.component_maps WHERE "index" = 'food_safety_logistics_vendor_tpe';
  SELECT id INTO v_logistics_ntpe_map_id FROM public.component_maps WHERE "index" = 'food_safety_logistics_vendor_ntpe';

  INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
  )
  SELECT
    'food_safety_market', NULL, ARRAY[v_market_tpe_map_id], '{}'::json, 'static', NULL,
    NULL, NULL, '臺北市市場處', '顯示臺北市公有市場分布。',
    '顯示臺北市各區公有零售市(商)場之空間分布，包含市場名稱、行政區與各營業種類攤位數。',
    '可用於食安稽查排程、市場周邊公共衛生服務配置、行政區市場分布比較，以及與人口、交通、醫療或災防圖層套疊分析。',
    ARRAY['https://data.taipei/dataset/detail?id=f490476d-d156-4492-a463-cf3405de3b55'],
    ARRAY['doit'], NOW(), NOW(), 'map_legend',
    $q$SELECT unnest(array['臺北市公有市場']) as name, unnest(array['circle']) as type, unnest(array[45]) as value$q$,
    NULL, 'taipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_safety_market' AND city = 'taipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_market_tpe_map_id],
    map_filter = '{}'::json,
    time_from = 'static',
    source = '臺北市市場處',
    short_desc = '顯示臺北市公有市場分布。',
    long_desc = '顯示臺北市各區公有零售市(商)場之空間分布，包含市場名稱、行政區與各營業種類攤位數。',
    use_case = '可用於食安稽查排程、市場周邊公共衛生服務配置、行政區市場分布比較，以及與人口、交通、醫療或災防圖層套疊分析。',
    links = ARRAY['https://data.taipei/dataset/detail?id=f490476d-d156-4492-a463-cf3405de3b55'],
    contributors = ARRAY['doit'],
    updated_at = NOW(),
    query_type = 'map_legend',
    query_chart = $q$SELECT unnest(array['臺北市公有市場']) as name, unnest(array['circle']) as type, unnest(array[45]) as value$q$,
    city = 'taipei'
  WHERE "index" = 'food_safety_market' AND city = 'taipei';

  INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
  )
  SELECT
    'food_safety_market', NULL, ARRAY[v_market_tpe_map_id, v_market_ntpe_map_id], '{}'::json, 'static', NULL,
    NULL, NULL, '臺北市市場處、新北市政府市場處', '顯示雙北公有市場分布。',
    '顯示臺北市各區公有零售市(商)場與新北市公有市場名冊之空間分布。',
    '可用於食安稽查排程、市場周邊公共衛生服務配置、跨區市場分布比較，以及與人口、交通、醫療或災防圖層套疊分析。',
    ARRAY[
      'https://data.taipei/dataset/detail?id=f490476d-d156-4492-a463-cf3405de3b55',
      'https://data.ntpc.gov.tw/datasets/785be91a-caaf-4e1c-91d6-f7d616d31a45'
    ],
    ARRAY['doit', 'ntpc'], NOW(), NOW(), 'map_legend',
    $q$SELECT unnest(array['臺北市公有市場','新北市公有市場']) as name,
             unnest(array['circle','circle']) as type,
             unnest(array[45,43]) as value$q$,
    NULL, 'metrotaipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_safety_market' AND city = 'metrotaipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_market_tpe_map_id, v_market_ntpe_map_id],
    map_filter = '{}'::json,
    time_from = 'static',
    source = '臺北市市場處、新北市政府市場處',
    short_desc = '顯示雙北公有市場分布。',
    long_desc = '顯示臺北市各區公有零售市(商)場與新北市公有市場名冊之空間分布。',
    use_case = '可用於食安稽查排程、市場周邊公共衛生服務配置、跨區市場分布比較，以及與人口、交通、醫療或災防圖層套疊分析。',
    links = ARRAY[
      'https://data.taipei/dataset/detail?id=f490476d-d156-4492-a463-cf3405de3b55',
      'https://data.ntpc.gov.tw/datasets/785be91a-caaf-4e1c-91d6-f7d616d31a45'
    ],
    contributors = ARRAY['doit', 'ntpc'],
    updated_at = NOW(),
    query_type = 'map_legend',
    query_chart = $q$SELECT unnest(array['臺北市公有市場','新北市公有市場']) as name,
                          unnest(array['circle','circle']) as type,
                          unnest(array[45,43]) as value$q$,
    city = 'metrotaipei'
  WHERE "index" = 'food_safety_market' AND city = 'metrotaipei';

  INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
  )
  SELECT
    'food_safety_logistics_vendor', NULL, ARRAY[v_logistics_tpe_map_id], '{}'::json, 'static', NULL,
    NULL, NULL, '衛生監管機構', '顯示臺北市食品物流業者分布。',
    '顯示臺北市 FDA 食品業者登錄中物流業者的地理分布。',
    '可用於食安稽查、物流節點盤點與食物供應鏈空間分析。',
    ARRAY['https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=臺北市'],
    ARRAY['doit'], NOW(), NOW(), 'map_legend',
    $q$SELECT unnest(array['臺北市食品物流業者']) as name, unnest(array['circle']) as type, unnest(array[256]) as value$q$,
    NULL, 'taipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_safety_logistics_vendor' AND city = 'taipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_logistics_tpe_map_id],
    map_filter = '{}'::json,
    time_from = 'static',
    source = '衛生監管機構',
    short_desc = '顯示臺北市食品物流業者分布。',
    long_desc = '顯示臺北市 FDA 食品業者登錄中物流業者的地理分布。',
    use_case = '可用於食安稽查、物流節點盤點與食物供應鏈空間分析。',
    links = ARRAY['https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=臺北市'],
    contributors = ARRAY['doit'],
    updated_at = NOW(),
    query_type = 'map_legend',
    query_chart = $q$SELECT unnest(array['臺北市食品物流業者']) as name, unnest(array['circle']) as type, unnest(array[256]) as value$q$,
    city = 'taipei'
  WHERE "index" = 'food_safety_logistics_vendor' AND city = 'taipei';

  INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
  )
  SELECT
    'food_safety_logistics_vendor', NULL, ARRAY[v_logistics_tpe_map_id, v_logistics_ntpe_map_id], '{}'::json, 'static', NULL,
    NULL, NULL, '衛生監管機構', '顯示雙北食品物流業者分布。',
    '顯示雙北 FDA 食品業者登錄中物流業者的地理分布。',
    '可用於食安稽查、物流節點盤點與食物供應鏈空間分析。',
    ARRAY[
      'https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=臺北市',
      'https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=新北市'
    ],
    ARRAY['doit', 'ntpc'], NOW(), NOW(), 'map_legend',
    $q$SELECT unnest(array['臺北市食品物流業者','新北市食品物流業者']) as name,
             unnest(array['circle','circle']) as type,
             unnest(array[256,479]) as value$q$,
    NULL, 'metrotaipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_safety_logistics_vendor' AND city = 'metrotaipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_logistics_tpe_map_id, v_logistics_ntpe_map_id],
    map_filter = '{}'::json,
    time_from = 'static',
    source = '衛生監管機構',
    short_desc = '顯示雙北食品物流業者分布。',
    long_desc = '顯示雙北 FDA 食品業者登錄中物流業者的地理分布。',
    use_case = '可用於食安稽查、物流節點盤點與食物供應鏈空間分析。',
    links = ARRAY[
      'https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=臺北市',
      'https://fadenbook.fda.gov.tw/pub/search-Vendor-County-result.aspx?city=新北市'
    ],
    contributors = ARRAY['doit', 'ntpc'],
    updated_at = NOW(),
    query_type = 'map_legend',
    query_chart = $q$SELECT unnest(array['臺北市食品物流業者','新北市食品物流業者']) as name,
                          unnest(array['circle','circle']) as type,
                          unnest(array[256,479]) as value$q$,
    city = 'metrotaipei'
  WHERE "index" = 'food_safety_logistics_vendor' AND city = 'metrotaipei';

  INSERT INTO public.dashboards ("index", name, components, icon, created_at, updated_at)
  SELECT
    'food-safety-health-tpe',
    '食安健康',
    array_remove(ARRAY[v_market_component_id, v_logistics_component_id], NULL),
    'restaurant_menu',
    NOW(),
    NOW()
  WHERE NOT EXISTS (
    SELECT 1 FROM public.dashboards WHERE "index" = 'food-safety-health-tpe'
  );

  UPDATE public.dashboards
  SET
    name = '食安健康',
    components = array_remove(ARRAY[v_market_component_id, v_logistics_component_id], NULL),
    icon = 'restaurant_menu',
    updated_at = NOW()
  WHERE "index" = 'food-safety-health-tpe';

  INSERT INTO public.dashboards ("index", name, components, icon, created_at, updated_at)
  SELECT
    'food-safety-health-metrotaipei',
    '食安健康',
    array_remove(ARRAY[v_market_component_id, v_logistics_component_id, v_fda_component_id], NULL),
    'restaurant_menu',
    NOW(),
    NOW()
  WHERE NOT EXISTS (
    SELECT 1 FROM public.dashboards WHERE "index" = 'food-safety-health-metrotaipei'
  );

  UPDATE public.dashboards
  SET
    name = '食安健康',
    components = array_remove(ARRAY[v_market_component_id, v_logistics_component_id, v_fda_component_id], NULL),
    icon = 'restaurant_menu',
    updated_at = NOW()
  WHERE "index" = 'food-safety-health-metrotaipei';

  SELECT id INTO v_tpe_dashboard_id FROM public.dashboards WHERE "index" = 'food-safety-health-tpe';
  SELECT id INTO v_metrotpe_dashboard_id FROM public.dashboards WHERE "index" = 'food-safety-health-metrotaipei';
  SELECT id INTO v_taipei_group_id FROM public.groups WHERE name = 'taipei';
  SELECT id INTO v_metrotaipei_group_id FROM public.groups WHERE name = 'metrotaipei';

  INSERT INTO public.dashboard_groups (dashboard_id, group_id)
  SELECT v_tpe_dashboard_id, v_taipei_group_id
  WHERE v_tpe_dashboard_id IS NOT NULL
    AND v_taipei_group_id IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM public.dashboard_groups WHERE dashboard_id = v_tpe_dashboard_id AND group_id = v_taipei_group_id
    );

  INSERT INTO public.dashboard_groups (dashboard_id, group_id)
  SELECT v_metrotpe_dashboard_id, v_metrotaipei_group_id
  WHERE v_metrotpe_dashboard_id IS NOT NULL
    AND v_metrotaipei_group_id IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM public.dashboard_groups WHERE dashboard_id = v_metrotpe_dashboard_id AND group_id = v_metrotaipei_group_id
    );
END $$;

COMMIT;
