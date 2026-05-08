BEGIN;

INSERT INTO public.component_charts ("index", color, types, unit)
VALUES (
  'food_safety_death_share',
  ARRAY['#D84C73', '#F5B041', '#4A90E2', '#8E63C7'],
  ARRAY['TimelineSeparateChart'],
  '%'
)
ON CONFLICT ("index") DO UPDATE
SET
  color = EXCLUDED.color,
  types = EXCLUDED.types,
  unit = EXCLUDED.unit;

INSERT INTO public.components (id, "index", name)
VALUES (503, 'food_safety_death_share', '主要死因占比統計')
ON CONFLICT (id) DO UPDATE
SET
  "index" = EXCLUDED."index",
  name = EXCLUDED.name;

DELETE FROM public.query_charts
WHERE "index" = 'food_safety_death_share';

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
VALUES
(
  'food_safety_death_share',
  NULL,
  ARRAY[]::integer[],
  '{}',
  'static',
  NULL,
  1,
  'year',
  '臺北市政府主計處',
  '顯示臺北市近 10 年主要死因死亡占比趨勢。',
  '此組件使用臺北市主要死因死亡率資料，將心臟疾病、糖尿病、腎炎腎徵候群及腎性病變、慢性肝病及肝硬化之死亡率除以所有死亡原因死亡率，轉換為占所有死亡原因之百分比，並以近 10 年趨勢作為主圖呈現。此指標是食安健康頁面的慢性病與主要死因背景指標，不代表食安事件直接歸因死亡。',
  '可用於觀察臺北市食安健康相關慢性病背景、與腹瀉就診、食品來源、市場、物流及衛生據點等組件交叉參考，輔助公共衛生風險溝通。',
  ARRAY['https://tsis.dbas.gov.taipei/statis/webMain.aspx?sys=220&ymf=8100&kind=21&type=0&funid=A05032801&cycle=4&outmode=12&compmode=0&outkind=1&deflst=2&nzo=1'],
  ARRAY['doit'],
  NOW(),
  NOW(),
  'time',
  'WITH causes(death_cause, sort_order) AS (VALUES (''心臟疾病'', 1), (''糖尿病'', 2), (''腎炎腎徵候群及腎性病變'', 3), (''慢性肝病及肝硬化'', 4)), latest_year AS (SELECT MAX(year) AS year FROM public.food_safety_death_cause_share WHERE city = ''臺北市'') SELECT MAKE_DATE(d.year, 1, 1)::timestamp AS x_axis, c.death_cause AS y_axis, ROUND(d.death_share_percent::numeric, 2)::float AS data FROM public.food_safety_death_cause_share d JOIN causes c ON c.death_cause = d.death_cause CROSS JOIN latest_year y WHERE d.city = ''臺北市'' AND d.year >= y.year - 9 ORDER BY d.year, c.sort_order',
  NULL,
  'taipei'
),
(
  'food_safety_death_share',
  NULL,
  ARRAY[]::integer[],
  '{}',
  'static',
  NULL,
  1,
  'year',
  '臺北市政府主計處、新北市政府主計處',
  '顯示雙北近 10 年主要死因死亡占比趨勢。',
  '此組件將臺北市主要死因死亡率與新北市主要死因死亡人數統一轉換為主要死因占所有死亡原因之百分比，並以近 10 年趨勢作為主圖呈現。臺北市以該死因死亡率除以所有死亡原因死亡率；新北市以該死因死亡人數除以所有死亡人數。此指標是食安健康頁面的慢性病與主要死因背景指標，不代表食安事件直接歸因死亡。',
  '可用於比較雙北主要死因占比背景，並與腹瀉就診、食品來源、市場、物流、衛生據點與水質等組件交叉參考，支援公共衛生風險盤點與政策溝通。',
  ARRAY['https://tsis.dbas.gov.taipei/statis/webMain.aspx?sys=220&ymf=8100&kind=21&type=0&funid=A05032801&cycle=4&outmode=12&compmode=0&outkind=1&deflst=2&nzo=1','https://data.ntpc.gov.tw/datasets/e490f906-93f0-4fc3-b5b3-fe34fb31d1db'],
  ARRAY['doit','ntpc'],
  NOW(),
  NOW(),
  'time',
  'WITH causes(death_cause, sort_order) AS (VALUES (''心臟疾病'', 1), (''糖尿病'', 2), (''腎炎腎徵候群及腎性病變'', 3), (''慢性肝病及肝硬化'', 4)), latest_year AS (SELECT city, MAX(year) AS year FROM public.food_safety_death_cause_share WHERE city IN (''臺北市'', ''新北市'') GROUP BY city) SELECT MAKE_DATE(d.year, 1, 1)::timestamp AS x_axis, c.death_cause || ''('' || CASE d.city WHEN ''臺北市'' THEN ''台北'' ELSE ''新北'' END || '')'' AS y_axis, ROUND(d.death_share_percent::numeric, 2)::float AS data FROM public.food_safety_death_cause_share d JOIN causes c ON c.death_cause = d.death_cause JOIN latest_year y ON y.city = d.city WHERE d.city IN (''臺北市'', ''新北市'') AND d.year >= y.year - 9 ORDER BY d.year, c.sort_order, CASE d.city WHEN ''臺北市'' THEN 1 ELSE 2 END',
  NULL,
  'metrotaipei'
);

UPDATE public.dashboards
SET
  components = CASE
    WHEN components IS NULL THEN ARRAY[503]
    WHEN 503 = ANY(components) THEN components
    ELSE components || 503
  END,
  updated_at = NOW()
WHERE "index" IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');

COMMIT;
