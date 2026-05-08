-- Food Allergen Classification Component Setup
-- Component ID: 504
-- Index: food_allergen_classification
-- Description: 食品過敏原分布（每公司抽樣30產品，LLM分類，品牌地理編碼）
-- Chart: MapLegend (circle: 總店家數/有過敏原/無過敏原) + DonutChart (donut: 過敏原分布)
-- Map: circle layer, geojson source, has_allergens boolean → red/green color match

BEGIN;

-- 1. Create data table in dashboard DB (run against postgres-data)
CREATE TABLE IF NOT EXISTS public.food_allergen_classification (
    id serial PRIMARY KEY,
    county text,
    company_name text,
    brand_name text,
    product_name text,
    ingredients text,
    has_allergens boolean,
    allergens text,
    allergen_count int,
    lat float,
    lon float,
    wkb_geometry geometry(Point, 4326),
    data_time timestamp,
    classified_at timestamp DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_food_allergen_company ON public.food_allergen_classification(company_name);
CREATE INDEX IF NOT EXISTS idx_food_allergen_brand ON public.food_allergen_classification(brand_name);
CREATE INDEX IF NOT EXISTS idx_food_allergen_geom ON public.food_allergen_classification USING GIST(wkb_geometry);

-- Auto-populate geometry from lat/lon
CREATE OR REPLACE FUNCTION update_food_allergen_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lat IS NOT NULL AND NEW.lon IS NOT NULL THEN
        NEW.wkb_geometry = public.ST_SetSRID(public.ST_MakePoint(NEW.lon, NEW.lat), 4326);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_food_allergen_geometry ON public.food_allergen_classification;
CREATE TRIGGER trigger_food_allergen_geometry
BEFORE INSERT OR UPDATE ON public.food_allergen_classification
FOR EACH ROW
EXECUTE FUNCTION update_food_allergen_geometry();

-- 2. Register component_maps (map layer config) in manager DB
INSERT INTO public.component_maps ("index", title, type, source, size, icon, paint, property)
SELECT
  'food_allergen_classification',
  '食品過敏原分布',
  'circle',
  'geojson',
  'small',
  NULL,
  '{
    "circle-color": ["case", ["boolean", ["get", "has_allergens"], false], "#ED6A45", "#4CB495"],
    "circle-opacity": 0.75,
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 2, 12, 4, 15, 7]
  }'::json,
  '[
    {"key":"county","name":"縣市"},
    {"key":"company_name","name":"公司名稱"},
    {"key":"brand_name","name":"品牌名稱"},
    {"key":"allergen_count","name":"過敏原種類數"},
    {"key":"allergens","name":"過敏原清單"},
    {"key":"has_allergens","name":"是否含過敏原"}
  ]'::json
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_maps WHERE "index" = 'food_allergen_classification'
);

UPDATE public.component_maps
SET
  title = '食品過敏原分布',
  type = 'circle',
  source = 'geojson',
  size = 'small',
  icon = NULL,
  paint = '{
    "circle-color": ["case", ["boolean", ["get", "has_allergens"], false], "#ED6A45", "#4CB495"],
    "circle-opacity": 0.75,
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 2, 12, 4, 15, 7]
  }'::json,
  property = '[
    {"key":"county","name":"縣市"},
    {"key":"company_name","name":"公司名稱"},
    {"key":"brand_name","name":"品牌名稱"},
    {"key":"allergen_count","name":"過敏原種類數"},
    {"key":"allergens","name":"過敏原清單"},
    {"key":"has_allergens","name":"是否含過敏原"}
  ]'::json
WHERE "index" = 'food_allergen_classification';

-- 3. Register component in manager DB
INSERT INTO public.components (id, "index", name)
VALUES (504, 'food_allergen_classification', '食品過敏原風險分類')
ON CONFLICT (id) DO UPDATE SET "index" = EXCLUDED."index", name = EXCLUDED.name;

-- 4. Register chart config: MapLegend + DonutChart with 8 colors
INSERT INTO public.component_charts ("index", color, types, unit)
VALUES (
    'food_allergen_classification',
    ARRAY['#ED6A45', '#4CB495', '#F2C94C', '#2D9CDB', '#9B51E0', '#EB5757', '#56CCF2', '#F2994A'],
    ARRAY['MapLegend', 'DonutChart'],
    '家'
)
ON CONFLICT ("index") DO UPDATE SET
    color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

-- 5. Register query_charts and attach to dashboards
-- MapLegend items (type='circle'): 總店家數, 有過敏原, 無過敏原
-- DonutChart items (type='donut'): 乳製品, 海鮮類, 麩質穀物, 花生, 酒精, 蠶豆
DO $$
DECLARE
  v_map_id integer;
  v_tpe_dashboard_id integer;
  v_metrotpe_dashboard_id integer;
BEGIN
  SELECT id INTO v_map_id FROM public.component_maps WHERE "index" = 'food_allergen_classification';

  -- taipei
  INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
  )
  SELECT
    'food_allergen_classification', NULL, ARRAY[v_map_id], '{}'::json, 'static', NULL,
    NULL, NULL, '臺北市政府開放資料平台',
    '顯示臺北市食品業者產品過敏原分布。',
    '此圖層彙整臺北市食品成分資料，每家公司抽樣30項產品，經LLM分類標註是否含有海鮮、乳製品、花生、麩質、蠶豆、酒精等特殊過敏原，並以品牌名稱進行地理編碼呈現空間分布。',
    '可用於食品過敏原風險地圖檢視、品牌過敏原分布比較、食安稽查重點區域規劃，以及與人口、醫療或教育圖層套疊分析。',
    ARRAY['https://data.taipei/dataset/detail?id=40900e11-3002-4c9b-9e23-aa3b72e3d46e'],
    ARRAY['doit'], NOW(), NOW(), 'map_legend',
    $q$SELECT name, type, value FROM (
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT brand_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true
      UNION ALL
      SELECT '無過敏原', 'circle', COUNT(DISTINCT brand_name)::int
      FROM public.food_allergen_classification WHERE has_allergens = false
      UNION ALL
      SELECT '乳製品' as name, 'donut' as type, COUNT(*)::int as value
      FROM public.food_allergen_classification WHERE allergens LIKE '%乳製品%'
      UNION ALL
      SELECT '海鮮類', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%海鮮類%'
      UNION ALL
      SELECT '麩質穀物', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%麩質穀物%'
      UNION ALL
      SELECT '花生', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%花生%'
      UNION ALL
      SELECT '酒精', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%酒精%'
      UNION ALL
      SELECT '蠶豆', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%蠶豆%'
    ) t ORDER BY type DESC, value DESC$q$,
    NULL, 'taipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_allergen_classification' AND city = 'taipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_map_id],
    map_filter = '{}'::json,
    time_from = 'static',
    source = '臺北市政府開放資料平台',
    short_desc = '顯示臺北市食品業者產品過敏原分布。',
    long_desc = '此圖層彙整臺北市食品成分資料，每家公司抽樣30項產品，經LLM分類標註是否含有海鮮、乳製品、花生、麩質、蠶豆、酒精等特殊過敏原，並以品牌名稱進行地理編碼呈現空間分布。',
    use_case = '可用於食品過敏原風險地圖檢視、品牌過敏原分布比較、食安稽查重點區域規劃，以及與人口、醫療或教育圖層套疊分析。',
    links = ARRAY['https://data.taipei/dataset/detail?id=40900e11-3002-4c9b-9e23-aa3b72e3d46e'],
    contributors = ARRAY['doit'],
    updated_at = NOW(),
    query_type = 'map_legend',
    query_chart = $q$SELECT name, type, value FROM (
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT brand_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true
      UNION ALL
      SELECT '無過敏原', 'circle', COUNT(DISTINCT brand_name)::int
      FROM public.food_allergen_classification WHERE has_allergens = false
      UNION ALL
      SELECT '乳製品' as name, 'donut' as type, COUNT(*)::int as value
      FROM public.food_allergen_classification WHERE allergens LIKE '%乳製品%'
      UNION ALL
      SELECT '海鮮類', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%海鮮類%'
      UNION ALL
      SELECT '麩質穀物', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%麩質穀物%'
      UNION ALL
      SELECT '花生', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%花生%'
      UNION ALL
      SELECT '酒精', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%酒精%'
      UNION ALL
      SELECT '蠶豆', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%蠶豆%'
    ) t ORDER BY type DESC, value DESC$q$,
    city = 'taipei'
  WHERE "index" = 'food_allergen_classification' AND city = 'taipei';

  -- metrotaipei (same Taipei-only data)
  INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
  )
  SELECT
    'food_allergen_classification', NULL, ARRAY[v_map_id], '{"mode":"byParam","byParam":{"xParam":"county"}}'::json, 'static', NULL,
    NULL, NULL, '臺北市政府開放資料平台',
    '顯示雙北食品業者產品過敏原分布。',
    '此圖層彙整雙北食品成分資料，每家公司抽樣30項產品，經LLM分類標註是否含有海鮮、乳製品、花生、麩質、蠶豆、酒精等特殊過敏原，並以品牌名稱進行地理編碼呈現空間分布。',
    '可用於食品過敏原風險地圖檢視、品牌過敏原分布比較、食安稽查重點區域規劃，以及與人口、醫療或教育圖層套疊分析。',
    ARRAY['https://data.taipei/dataset/detail?id=40900e11-3002-4c9b-9e23-aa3b72e3d46e'],
    ARRAY['doit'], NOW(), NOW(), 'map_legend',
    $q$SELECT name, type, value FROM (
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT brand_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '無過敏原', 'circle', COUNT(DISTINCT brand_name)::int
      FROM public.food_allergen_classification WHERE has_allergens = false AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '乳製品' as name, 'donut' as type, COUNT(*)::int as value
      FROM public.food_allergen_classification WHERE allergens LIKE '%乳製品%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '海鮮類', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%海鮮類%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '麩質穀物', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%麩質穀物%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '花生', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%花生%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '酒精', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%酒精%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '蠶豆', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%蠶豆%' AND county IN ('臺北市', '新北市')
    ) t ORDER BY type DESC, value DESC$q$,
    NULL, 'metrotaipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_allergen_classification' AND city = 'metrotaipei'
  );

  UPDATE public.query_charts
  SET
    map_config_ids = ARRAY[v_map_id],
    map_filter = '{"mode":"byParam","byParam":{"xParam":"county"}}'::json,
    time_from = 'static',
    source = '臺北市政府開放資料平台',
    short_desc = '顯示雙北食品業者產品過敏原分布。',
    long_desc = '此圖層彙整雙北食品成分資料，每家公司抽樣30項產品，經LLM分類標註是否含有海鮮、乳製品、花生、麩質、蠶豆、酒精等特殊過敏原，並以品牌名稱進行地理編碼呈現空間分布。',
    use_case = '可用於食品過敏原風險地圖檢視、品牌過敏原分布比較、食安稽查重點區域規劃，以及與人口、醫療或教育圖層套疊分析。',
    links = ARRAY['https://data.taipei/dataset/detail?id=40900e11-3002-4c9b-9e23-aa3b72e3d46e'],
    contributors = ARRAY['doit'],
    updated_at = NOW(),
    query_type = 'map_legend',
    query_chart = $q$SELECT name, type, value FROM (
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT brand_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '無過敏原', 'circle', COUNT(DISTINCT brand_name)::int
      FROM public.food_allergen_classification WHERE has_allergens = false AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '乳製品' as name, 'donut' as type, COUNT(*)::int as value
      FROM public.food_allergen_classification WHERE allergens LIKE '%乳製品%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '海鮮類', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%海鮮類%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '麩質穀物', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%麩質穀物%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '花生', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%花生%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '酒精', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%酒精%' AND county IN ('臺北市', '新北市')
      UNION ALL
      SELECT '蠶豆', 'donut', COUNT(*)::int
      FROM public.food_allergen_classification WHERE allergens LIKE '%蠶豆%' AND county IN ('臺北市', '新北市')
    ) t ORDER BY type DESC, value DESC$q$,
    city = 'metrotaipei'
  WHERE "index" = 'food_allergen_classification' AND city = 'metrotaipei';

  -- Attach to dashboards (use underscore index, not hyphen)
  SELECT id INTO v_tpe_dashboard_id FROM public.dashboards WHERE "index" = 'food_safety_health_tpe';
  SELECT id INTO v_metrotpe_dashboard_id FROM public.dashboards WHERE "index" = 'food_safety_health_metrotaipei';

  UPDATE public.dashboards
  SET components = array_append(components, 504),
      updated_at = NOW()
  WHERE id = v_tpe_dashboard_id
    AND NOT (504 = ANY(components));

  UPDATE public.dashboards
  SET components = array_append(components, 504),
      updated_at = NOW()
  WHERE id = v_metrotpe_dashboard_id
    AND NOT (504 = ANY(components));
END $$;

-- 6. Final display/map overrides
-- Use product-item counts for this product-level dataset, split map sources by city scope,
-- and keep map popup fields focused on point-level details.
DO $$
DECLARE
  v_map_id integer;
  v_tpe_map_id integer;
  v_metro_map_id integer;
BEGIN
  UPDATE public.component_charts
  SET unit = '項',
      color = ARRAY['#ED6A45', '#4CB495', '#F2C94C', '#2D9CDB', '#9B51E0', '#EB5757', '#56CCF2', '#F2994A'],
      types = ARRAY['MapLegend', 'DonutChart']
  WHERE "index" = 'food_allergen_classification';

  SELECT id INTO v_map_id
  FROM public.component_maps
  WHERE "index" = 'food_allergen_classification'
  LIMIT 1;

  UPDATE public.component_maps
  SET "index" = 'food_allergen_classification_tpe',
      title = '臺北市食品過敏原分布',
      type = 'circle',
      source = 'geojson',
      size = 'small',
      icon = NULL,
      paint = '{"circle-color":["case",["boolean",["get","has_allergens"],false],"#ED6A45","#4CB495"],"circle-opacity":0.75,"circle-stroke-color":"#ffffff","circle-stroke-width":1,"circle-radius":["interpolate",["linear"],["zoom"],9,2,12,4,15,7]}'::json,
      property = '[{"key":"county","name":"縣市"},{"key":"company_name","name":"公司名稱"},{"key":"brand_name","name":"品牌名稱"},{"key":"product_name","name":"產品名稱"},{"key":"has_allergens","name":"是否含過敏原"},{"key":"allergens","name":"過敏原清單"}]'::json
  WHERE id = v_map_id;

  INSERT INTO public.component_maps ("index", title, type, source, size, icon, paint, property)
  SELECT 'food_allergen_classification_metrotaipei', '雙北食品過敏原分布', 'circle', 'geojson', 'small', NULL,
         '{"circle-color":["case",["boolean",["get","has_allergens"],false],"#ED6A45","#4CB495"],"circle-opacity":0.75,"circle-stroke-color":"#ffffff","circle-stroke-width":1,"circle-radius":["interpolate",["linear"],["zoom"],9,2,12,4,15,7]}'::json,
         '[{"key":"county","name":"縣市"},{"key":"company_name","name":"公司名稱"},{"key":"brand_name","name":"品牌名稱"},{"key":"product_name","name":"產品名稱"},{"key":"has_allergens","name":"是否含過敏原"},{"key":"allergens","name":"過敏原清單"}]'::json
  WHERE NOT EXISTS (
    SELECT 1 FROM public.component_maps WHERE "index" = 'food_allergen_classification_metrotaipei'
  );

  SELECT id INTO v_tpe_map_id FROM public.component_maps WHERE "index" = 'food_allergen_classification_tpe' LIMIT 1;
  SELECT id INTO v_metro_map_id FROM public.component_maps WHERE "index" = 'food_allergen_classification_metrotaipei' LIMIT 1;

  UPDATE public.query_charts
  SET map_config_ids = ARRAY[v_tpe_map_id],
      map_filter = '{}'::json,
      query_chart = $q$SELECT name, type, value FROM (SELECT 1 AS sort_order, '無過敏原' AS name, 'circle' AS type, COUNT(*)::int AS value FROM public.food_allergen_classification WHERE county = '臺北市' AND has_allergens = false UNION ALL SELECT 2, '有過敏原', 'circle', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND has_allergens = true UNION ALL SELECT 10, '乳製品', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND allergens LIKE '%乳製品%' UNION ALL SELECT 10, '海鮮類', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND allergens LIKE '%海鮮類%' UNION ALL SELECT 10, '麩質穀物', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND allergens LIKE '%麩質穀物%' UNION ALL SELECT 10, '花生', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND allergens LIKE '%花生%' UNION ALL SELECT 10, '酒精', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND allergens LIKE '%酒精%' UNION ALL SELECT 10, '蠶豆', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county = '臺北市' AND allergens LIKE '%蠶豆%') t ORDER BY sort_order, value DESC$q$,
      updated_at = NOW()
  WHERE "index" = 'food_allergen_classification' AND city = 'taipei';

  UPDATE public.query_charts
  SET map_config_ids = ARRAY[v_metro_map_id],
      map_filter = '{}'::json,
      query_chart = $q$SELECT name, type, value FROM (SELECT 1 AS sort_order, '無過敏原' AS name, 'circle' AS type, COUNT(*)::int AS value FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND has_allergens = false UNION ALL SELECT 2, '有過敏原', 'circle', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND has_allergens = true UNION ALL SELECT 10, '乳製品', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND allergens LIKE '%乳製品%' UNION ALL SELECT 10, '海鮮類', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND allergens LIKE '%海鮮類%' UNION ALL SELECT 10, '麩質穀物', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND allergens LIKE '%麩質穀物%' UNION ALL SELECT 10, '花生', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND allergens LIKE '%花生%' UNION ALL SELECT 10, '酒精', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND allergens LIKE '%酒精%' UNION ALL SELECT 10, '蠶豆', 'donut', COUNT(*)::int FROM public.food_allergen_classification WHERE county IN ('臺北市','新北市') AND allergens LIKE '%蠶豆%') t ORDER BY sort_order, value DESC$q$,
      updated_at = NOW()
  WHERE "index" = 'food_allergen_classification' AND city = 'metrotaipei';
END $$;

COMMIT;
