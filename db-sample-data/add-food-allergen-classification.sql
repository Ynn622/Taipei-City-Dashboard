-- Food Allergen Classification Component Setup
-- Component ID: 504
-- Index: food_allergen_classification
-- Description: 食品過敏原分布（每公司抽樣30產品，LLM分類，品牌地理編碼）

BEGIN;

-- 1. Create data table in dashboard DB (run against postgres-data)
CREATE TABLE IF NOT EXISTS public.food_allergen_classification (
    id serial PRIMARY KEY,
    company_name text,
    brand_name text,
    product_name text,
    ingredients text[],
    has_allergens boolean,
    allergens text[],
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
        NEW.wkb_geometry = ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326);
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
    "circle-color": ["match", ["get", "has_allergens"], true, "#ED6A45", "#4CB495"],
    "circle-opacity": 0.75,
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["coalesce", ["to-number", ["get", "allergen_count"]], 0], 0, 4, 1, 6, 3, 10, 5, 14]
  }'::json,
  '[
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
    "circle-color": ["match", ["get", "has_allergens"], true, "#ED6A45", "#4CB495"],
    "circle-opacity": 0.75,
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1,
    "circle-radius": ["interpolate", ["linear"], ["coalesce", ["to-number", ["get", "allergen_count"]], 0], 0, 4, 1, 6, 3, 10, 5, 14]
  }'::json,
  property = '[
    {"key":"company_name","name":"公司名稱"},
    {"key":"brand_name","name":"品牌名稱"},
    {"key":"allergen_count","name":"過敏原種類數"},
    {"key":"allergens","name":"過敏原清單"},
    {"key":"has_allergens","name":"是否含過敏原"}
  ]'::json
WHERE "index" = 'food_allergen_classification';

-- 3. Register component in manager DB
INSERT INTO public.components (id, "index", name)
VALUES (504, 'food_allergen_classification', '食品過敏原分布')
ON CONFLICT (id) DO UPDATE SET "index" = EXCLUDED."index", name = EXCLUDED.name;

INSERT INTO public.component_charts ("index", color, types, unit)
VALUES (
    'food_allergen_classification',
    ARRAY['#ED6A45', '#4CB495'],
    ARRAY['MapLegend'],
    '家'
)
ON CONFLICT ("index") DO UPDATE SET
    color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

-- 4. Register query_charts and attach to dashboards
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
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true
      UNION ALL
      SELECT '無過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = false
    ) t$q$,
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
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true
      UNION ALL
      SELECT '無過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = false
    ) t$q$,
    city = 'taipei'
  WHERE "index" = 'food_allergen_classification' AND city = 'taipei';

  -- metrotaipei (same Taipei-only data)
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
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true
      UNION ALL
      SELECT '無過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = false
    ) t$q$,
    NULL, 'metrotaipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts WHERE "index" = 'food_allergen_classification' AND city = 'metrotaipei'
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
      SELECT '有過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = true
      UNION ALL
      SELECT '無過敏原' as name, 'circle' as type, COUNT(DISTINCT company_name)::int as value
      FROM public.food_allergen_classification WHERE has_allergens = false
    ) t$q$,
    city = 'metrotaipei'
  WHERE "index" = 'food_allergen_classification' AND city = 'metrotaipei';

  -- Attach to dashboards
  SELECT id INTO v_tpe_dashboard_id FROM public.dashboards WHERE "index" = 'food-safety-health-tpe';
  SELECT id INTO v_metrotpe_dashboard_id FROM public.dashboards WHERE "index" = 'food-safety-health-metrotaipei';

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

COMMIT;
