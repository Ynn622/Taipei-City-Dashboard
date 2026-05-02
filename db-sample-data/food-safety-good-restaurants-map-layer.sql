BEGIN;

INSERT INTO public.component_maps (
  "index",
  title,
  type,
  source,
  size,
  icon,
  paint,
  property
)
SELECT
  'fda_good_restaurants',
  '優良餐廳',
  'circle',
  'geojson',
  'small',
  NULL,
  '{
    "circle-color": [
      "match",
      ["get", "rating_result"],
      "優", "#5FB878",
      "良", "#F2B84B",
      "#9E9E9E"
    ],
    "circle-radius": 6,
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1
  }'::json,
  '[
    {"key": "restaurant_name", "name": "店名"},
    {"key": "address", "name": "地址"},
    {"key": "rating_result", "name": "評分結果"},
    {"key": "award_year", "name": "年度"}
  ]'::json
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_maps WHERE "index" = 'fda_good_restaurants'
);

UPDATE public.component_maps
SET
  title = '優良餐廳',
  type = 'circle',
  source = 'geojson',
  size = 'small',
  paint = '{
    "circle-color": [
      "match",
      ["get", "rating_result"],
      "優", "#5FB878",
      "良", "#F2B84B",
      "#9E9E9E"
    ],
    "circle-radius": 6,
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1
  }'::json,
  property = '[
    {"key": "restaurant_name", "name": "店名"},
    {"key": "address", "name": "地址"},
    {"key": "rating_result", "name": "評分結果"},
    {"key": "award_year", "name": "年度"}
  ]'::json
WHERE "index" = 'fda_good_restaurants';

INSERT INTO public.components ("index", name)
SELECT 'fda_good_restaurants', '優良餐廳'
WHERE NOT EXISTS (
  SELECT 1 FROM public.components WHERE "index" = 'fda_good_restaurants'
);

UPDATE public.components
SET name = '優良餐廳'
WHERE "index" = 'fda_good_restaurants';

INSERT INTO public.component_charts ("index", color, types, unit)
SELECT
  'fda_good_restaurants',
  ARRAY['#5FB878', '#F2B84B'],
  ARRAY['DistrictChart', 'RankListChart', 'TreemapChart'],
  '家'
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_charts WHERE "index" = 'fda_good_restaurants'
);

UPDATE public.component_charts
SET
  color = ARRAY['#5FB878', '#F2B84B'],
  types = ARRAY['DistrictChart', 'RankListChart', 'TreemapChart'],
  unit = '家'
WHERE "index" = 'fda_good_restaurants';

DO $$
DECLARE
  v_map_id integer;
  v_component_id integer;
  v_dashboard_id integer;
  v_group_id integer;
BEGIN
  SELECT id INTO v_map_id
  FROM public.component_maps
  WHERE "index" = 'fda_good_restaurants';

  SELECT id INTO v_component_id
  FROM public.components
  WHERE "index" = 'fda_good_restaurants';

  INSERT INTO public.query_charts (
    "index",
    history_config,
    map_config_ids,
    map_filter,
    time_from,
    time_to,
    update_freq,
    update_freq_unit,
    source,
    short_desc,
    long_desc,
    use_case,
    links,
    contributors,
    created_at,
    updated_at,
    query_type,
    query_chart,
    query_history,
    city
  )
  SELECT
    'fda_good_restaurants',
    NULL,
    ARRAY[v_map_id],
    '{"mode":"byParam","byParam":{"xParam":"district"}}'::json,
    'static',
    NULL,
    NULL,
    NULL,
    '衛生監管機構',
    '顯示雙北最新年度評核結果為優或良的優良餐廳點位。',
    '此圖層彙整臺北市與新北市最新年度優良餐廳資料，包含店名、地址、經緯度與評分結果，並僅保留資料來源可取得之最新年度資料。',
    '可用於食安健康服務查詢、餐飲環境品質觀察、商圈餐飲設施盤點，以及與人口、交通或觀光圖層套疊分析。',
    ARRAY[
      'https://foodtracer.health.ntpc.gov.tw/w/foodtracer/FoodAward',
      'https://data.gov.tw/dataset/145738'
    ],
    ARRAY['doit', 'ntpc'],
    NOW(),
    NOW(),
    'three_d',
    'WITH district_order(district, sort_order) AS (
       VALUES
         (''北投區'', 1), (''士林區'', 2), (''內湖區'', 3), (''南港區'', 4),
         (''松山區'', 5), (''信義區'', 6), (''中山區'', 7), (''大同區'', 8),
         (''中正區'', 9), (''萬華區'', 10), (''大安區'', 11), (''文山區'', 12),
         (''新莊區'', 13), (''淡水區'', 14), (''汐止區'', 15), (''板橋區'', 16),
         (''三重區'', 17), (''樹林區'', 18), (''土城區'', 19), (''蘆洲區'', 20),
         (''中和區'', 21), (''永和區'', 22), (''新店區'', 23), (''鶯歌區'', 24),
         (''三峽區'', 25), (''瑞芳區'', 26), (''五股區'', 27), (''泰山區'', 28),
         (''林口區'', 29), (''深坑區'', 30), (''石碇區'', 31), (''坪林區'', 32),
         (''三芝區'', 33), (''石門區'', 34), (''八里區'', 35), (''平溪區'', 36),
         (''雙溪區'', 37), (''貢寮區'', 38), (''金山區'', 39), (''萬里區'', 40),
         (''烏來區'', 41)
     ),
     ratings(rating_result, rating_order) AS (
       VALUES (''優'', 1), (''良'', 2)
     ),
     aggregated AS (
       SELECT district, rating_result, COUNT(*)::int AS data
       FROM public.fda_good_restaurants
       WHERE award_year = (SELECT MAX(award_year) FROM public.fda_good_restaurants)
       GROUP BY district, rating_result
     )
     SELECT
       d.district AS x_axis,
       r.rating_result AS y_axis,
       COALESCE(a.data, 0)::int AS data
     FROM district_order d
     CROSS JOIN ratings r
     LEFT JOIN aggregated a
       ON a.district = d.district
      AND a.rating_result = r.rating_result
     ORDER BY d.sort_order, r.rating_order',
    NULL,
    'metrotaipei'
  WHERE NOT EXISTS (
    SELECT 1
    FROM public.query_charts
    WHERE "index" = 'fda_good_restaurants'
      AND city = 'metrotaipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_map_id],
    map_filter = '{"mode":"byParam","byParam":{"xParam":"district"}}'::json,
    time_from = 'static',
    source = '衛生監管機構',
    short_desc = '顯示雙北最新年度評核結果為優或良的優良餐廳點位。',
    long_desc = '此圖層彙整臺北市與新北市最新年度優良餐廳資料，包含店名、地址、經緯度與評分結果，並僅保留資料來源可取得之最新年度資料。',
    use_case = '可用於食安健康服務查詢、餐飲環境品質觀察、商圈餐飲設施盤點，以及與人口、交通或觀光圖層套疊分析。',
    links = ARRAY[
      'https://foodtracer.health.ntpc.gov.tw/w/foodtracer/FoodAward',
      'https://data.gov.tw/dataset/145738'
    ],
    contributors = ARRAY['doit', 'ntpc'],
    updated_at = NOW(),
    query_type = 'three_d',
    query_chart = 'WITH district_order(district, sort_order) AS (
       VALUES
         (''北投區'', 1), (''士林區'', 2), (''內湖區'', 3), (''南港區'', 4),
         (''松山區'', 5), (''信義區'', 6), (''中山區'', 7), (''大同區'', 8),
         (''中正區'', 9), (''萬華區'', 10), (''大安區'', 11), (''文山區'', 12),
         (''新莊區'', 13), (''淡水區'', 14), (''汐止區'', 15), (''板橋區'', 16),
         (''三重區'', 17), (''樹林區'', 18), (''土城區'', 19), (''蘆洲區'', 20),
         (''中和區'', 21), (''永和區'', 22), (''新店區'', 23), (''鶯歌區'', 24),
         (''三峽區'', 25), (''瑞芳區'', 26), (''五股區'', 27), (''泰山區'', 28),
         (''林口區'', 29), (''深坑區'', 30), (''石碇區'', 31), (''坪林區'', 32),
         (''三芝區'', 33), (''石門區'', 34), (''八里區'', 35), (''平溪區'', 36),
         (''雙溪區'', 37), (''貢寮區'', 38), (''金山區'', 39), (''萬里區'', 40),
         (''烏來區'', 41)
     ),
     ratings(rating_result, rating_order) AS (
       VALUES (''優'', 1), (''良'', 2)
     ),
     aggregated AS (
       SELECT district, rating_result, COUNT(*)::int AS data
       FROM public.fda_good_restaurants
       WHERE award_year = (SELECT MAX(award_year) FROM public.fda_good_restaurants)
       GROUP BY district, rating_result
     )
     SELECT
       d.district AS x_axis,
       r.rating_result AS y_axis,
       COALESCE(a.data, 0)::int AS data
     FROM district_order d
     CROSS JOIN ratings r
     LEFT JOIN aggregated a
       ON a.district = d.district
      AND a.rating_result = r.rating_result
     ORDER BY d.sort_order, r.rating_order',
    city = 'metrotaipei'
  WHERE "index" = 'fda_good_restaurants'
    AND city = 'metrotaipei';

  INSERT INTO public.dashboards (
    "index",
    name,
    components,
    icon,
    created_at,
    updated_at
  )
  SELECT
    'food_safety_health_metrotaipei',
    '食安健康',
    ARRAY[v_component_id],
    'restaurant_menu',
    NOW(),
    NOW()
  WHERE NOT EXISTS (
    SELECT 1
    FROM public.dashboards
    WHERE "index" = 'food_safety_health_metrotaipei'
  );

  UPDATE public.dashboards
  SET
    name = '食安健康',
    components = CASE
      WHEN components IS NULL THEN ARRAY[v_component_id]
      WHEN v_component_id = ANY(components) THEN components
      ELSE components || v_component_id
    END,
    icon = 'restaurant_menu',
    updated_at = NOW()
  WHERE "index" = 'food_safety_health_metrotaipei';

  SELECT id INTO v_dashboard_id
  FROM public.dashboards
  WHERE "index" = 'food_safety_health_metrotaipei';

  SELECT id INTO v_group_id
  FROM public.groups
  WHERE name = 'metrotaipei'
    AND is_personal = false;

  IF v_group_id IS NULL THEN
    RAISE EXCEPTION 'Cannot find non-personal group: metrotaipei';
  END IF;

  INSERT INTO public.dashboard_groups (dashboard_id, group_id)
  SELECT v_dashboard_id, v_group_id
  WHERE NOT EXISTS (
    SELECT 1
    FROM public.dashboard_groups
    WHERE dashboard_id = v_dashboard_id
      AND group_id = v_group_id
  );

  DELETE FROM public.dashboard_groups
  WHERE dashboard_id IN (
    SELECT id
    FROM public.dashboards
    WHERE "index" = 'food-safety-health-metrotaipei'
  );

  DELETE FROM public.dashboards
  WHERE "index" = 'food-safety-health-metrotaipei';
END $$;

COMMIT;
