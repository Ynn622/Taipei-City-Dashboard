-- Food Processing Pass Rate Component Setup
-- Component ID: 505
-- Index: food_processing_pass_rate
-- Description: 加工食品不合格率 (105-114年，雙北，五大類)

BEGIN;

-- 1. Create data table in dashboard DB (run against postgres-data)
CREATE TABLE IF NOT EXISTS public.food_processing_pass_rate (
    year int,
    county text,
    category text,
    inspection_count int,
    non_compliant_count int,
    pass_rate float
);

-- 2. Register component in manager DB (run against postgres-manager)
INSERT INTO public.components (id, "index", name)
VALUES (505, 'food_processing_pass_rate', '加工食品不合格率統計')
ON CONFLICT (id) DO UPDATE SET "index" = EXCLUDED."index", name = EXCLUDED.name;

INSERT INTO public.component_charts ("index", color, types, unit)
VALUES (
    'food_processing_pass_rate',
    ARRAY['#4CB495', '#F5C860', '#ED6A45', '#1E88E5', '#8E63C7'],
    ARRAY['TimelineSeparateChart'],
    '%'
)
ON CONFLICT ("index") DO UPDATE SET
    color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit = EXCLUDED.unit;

-- 3. Query charts: taipei
INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
)
SELECT
    'food_processing_pass_rate',
    '{"range":["max"],"color":["#4CB495","#F5C860","#ED6A45","#1E88E5","#8E63C7"],"unit":"%"}'::json,
    ARRAY[]::integer[], '{}'::json, 'static', NULL, 1, 'year',
    '衛生福利部食品藥物管理署',
    '顯示臺北市加工食品不合格率歷年趨勢（105-114年）。',
    '此組件彙整衛生福利部食品衛生管理工作資料，篩選肉品、蛋品、水產、蔬果及食品添加物五大類，計算各年度不合格率並以折線圖呈現趨勢。',
    '可用於觀察臺北市加工食品安全品質的長期變化趨勢，輔助食安政策評估與稽查資源配置。',
    ARRAY['https://www.mohw.gov.tw/dl-38807-41ca6849-eccd-418a-95f5-20649b0c5bf9.html'],
    ARRAY['doit'], NOW(), NOW(), 'time',
    $chart$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((non_compliant_count::float / NULLIF(inspection_count, 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county = '臺北市' ORDER BY year, category$chart$,
    $hist$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((non_compliant_count::float / NULLIF(inspection_count, 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county = '臺北市' ORDER BY year, category$hist$,
    'taipei'
WHERE NOT EXISTS (SELECT 1 FROM public.query_charts WHERE "index" = 'food_processing_pass_rate' AND city = 'taipei');

UPDATE public.query_charts SET
    query_chart = $chart$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((non_compliant_count::float / NULLIF(inspection_count, 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county = '臺北市' ORDER BY year, category$chart$,
    query_history = $hist$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((non_compliant_count::float / NULLIF(inspection_count, 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county = '臺北市' ORDER BY year, category$hist$,
    links = ARRAY['https://www.mohw.gov.tw/dl-38807-41ca6849-eccd-418a-95f5-20649b0c5bf9.html']
WHERE "index" = 'food_processing_pass_rate' AND city = 'taipei';

-- 4. Query charts: metrotaipei
INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
)
SELECT
    'food_processing_pass_rate',
    '{"range":["max"],"color":["#4CB495","#F5C860","#ED6A45","#1E88E5","#8E63C7"],"unit":"%"}'::json,
    ARRAY[]::integer[], '{}'::json, 'static', NULL, 1, 'year',
    '衛生福利部食品藥物管理署',
    '顯示雙北加工食品不合格率歷年趨勢（105-114年）。',
    '此組件彙整衛生福利部食品衛生管理工作資料，篩選肉品、蛋品、水產、蔬果及食品添加物五大類，計算雙北各年度不合格率並以折線圖呈現趨勢。',
    '可用於觀察雙北加工食品安全品質的長期變化趨勢，輔助跨區食安政策評估與稽查資源配置。',
    ARRAY['https://www.mohw.gov.tw/dl-38807-41ca6849-eccd-418a-95f5-20649b0c5bf9.html'],
    ARRAY['doit'], NOW(), NOW(), 'time',
    $chart$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((SUM(non_compliant_count)::float / NULLIF(SUM(inspection_count), 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county IN ('臺北市', '新北市') GROUP BY year, category ORDER BY year, category$chart$,
    $hist$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((SUM(non_compliant_count)::float / NULLIF(SUM(inspection_count), 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county IN ('臺北市', '新北市') GROUP BY year, category ORDER BY year, category$hist$,
    'metrotaipei'
WHERE NOT EXISTS (SELECT 1 FROM public.query_charts WHERE "index" = 'food_processing_pass_rate' AND city = 'metrotaipei');

UPDATE public.query_charts SET
    query_chart = $chart$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((SUM(non_compliant_count)::float / NULLIF(SUM(inspection_count), 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county IN ('臺北市', '新北市') GROUP BY year, category ORDER BY year, category$chart$,
    query_history = $hist$SELECT MAKE_DATE(year + 1911, 1, 1)::timestamp AS x_axis, category AS y_axis, ROUND((SUM(non_compliant_count)::float / NULLIF(SUM(inspection_count), 0) * 100))::numeric AS data FROM public.food_processing_pass_rate WHERE county IN ('臺北市', '新北市') GROUP BY year, category ORDER BY year, category$hist$,
    links = ARRAY['https://www.mohw.gov.tw/dl-38807-41ca6849-eccd-418a-95f5-20649b0c5bf9.html']
WHERE "index" = 'food_processing_pass_rate' AND city = 'metrotaipei';

-- 5. Attach component to dashboards
UPDATE public.dashboards
SET components = array_append(components, 505),
    updated_at = NOW()
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei')
  AND NOT (505 = ANY(components));

-- 6. Insert data (105-114年, 臺北市+新北市, 五大類)
INSERT INTO public.food_processing_pass_rate (year, county, category, inspection_count, non_compliant_count, pass_rate) VALUES
    (105, '新北市', '肉品類', 1349, 13, 99.04),
    (105, '新北市', '蛋品類', 393, 32, 91.86),
    (105, '新北市', '水產類', 711, 16, 97.75),
    (105, '新北市', '蔬果類', 0, 0, 0),
    (105, '新北市', '添加物', 516, 1, 99.81),
    (105, '臺北市', '肉品類', 4591, 7, 99.85),
    (105, '臺北市', '蛋品類', 1843, 3, 99.84),
    (105, '臺北市', '水產類', 3202, 11, 99.66),
    (105, '臺北市', '蔬果類', 0, 0, 0),
    (105, '臺北市', '添加物', 761, 6, 99.21),
    (106, '新北市', '肉品類', 1284, 15, 98.83),
    (106, '新北市', '蛋品類', 383, 8, 97.91),
    (106, '新北市', '水產類', 1060, 13, 98.77),
    (106, '新北市', '蔬果類', 0, 0, 0),
    (106, '新北市', '添加物', 565, 0, 100.0),
    (106, '臺北市', '肉品類', 3970, 10, 99.75),
    (106, '臺北市', '蛋品類', 2054, 5, 99.76),
    (106, '臺北市', '水產類', 3977, 13, 99.67),
    (106, '臺北市', '蔬果類', 0, 0, 0),
    (106, '臺北市', '添加物', 531, 6, 98.87),
    (107, '新北市', '肉品類', 1210, 14, 98.84),
    (107, '新北市', '蛋品類', 459, 5, 98.91),
    (107, '新北市', '水產類', 3006, 8, 99.73),
    (107, '新北市', '蔬果類', 0, 0, 0),
    (107, '新北市', '添加物', 1335, 0, 100.0),
    (107, '臺北市', '肉品類', 1825, 10, 99.45),
    (107, '臺北市', '蛋品類', 171, 8, 95.32),
    (107, '臺北市', '水產類', 1160, 17, 98.53),
    (107, '臺北市', '蔬果類', 0, 0, 0),
    (107, '臺北市', '添加物', 77, 10, 87.01),
    (108, '新北市', '肉品類', 1906, 10, 99.48),
    (108, '新北市', '蛋品類', 460, 2, 99.57),
    (108, '新北市', '水產類', 1094, 10, 99.09),
    (108, '新北市', '蔬果類', 3158, 29, 99.08),
    (108, '新北市', '添加物', 263, 1, 99.62),
    (108, '臺北市', '肉品類', 1659, 1, 99.94),
    (108, '臺北市', '蛋品類', 256, 1, 99.61),
    (108, '臺北市', '水產類', 640, 11, 98.28),
    (108, '臺北市', '蔬果類', 2291, 127, 94.46),
    (108, '臺北市', '添加物', 55, 0, 100.0),
    (109, '新北市', '肉品類', 6371, 0, 100.0),
    (109, '新北市', '蛋品類', 219, 1, 99.54),
    (109, '新北市', '水產類', 1375, 4, 99.71),
    (109, '新北市', '蔬果類', 2671, 19, 99.29),
    (109, '新北市', '添加物', 304, 0, 100.0),
    (109, '臺北市', '肉品類', 3611, 6, 99.83),
    (109, '臺北市', '蛋品類', 159, 4, 97.48),
    (109, '臺北市', '水產類', 688, 9, 98.69),
    (109, '臺北市', '蔬果類', 4039, 99, 97.55),
    (109, '臺北市', '添加物', 30, 1, 96.67),
    (110, '新北市', '肉品類', 16044, 11, 99.93),
    (110, '新北市', '蛋品類', 274, 2, 99.27),
    (110, '新北市', '水產類', 3785, 7, 99.82),
    (110, '新北市', '蔬果類', 3727, 44, 98.82),
    (110, '新北市', '添加物', 531, 0, 100.0),
    (110, '臺北市', '肉品類', 9569, 24, 99.75),
    (110, '臺北市', '蛋品類', 120, 4, 96.67),
    (110, '臺北市', '水產類', 947, 31, 96.73),
    (110, '臺北市', '蔬果類', 3910, 107, 97.26),
    (110, '臺北市', '添加物', 20, 1, 95.0),
    (111, '新北市', '肉品類', 15075, 8, 99.95),
    (111, '新北市', '蛋品類', 533, 0, 100.0),
    (111, '新北市', '水產類', 8620, 5, 99.94),
    (111, '新北市', '蔬果類', 7495, 49, 99.35),
    (111, '新北市', '添加物', 782, 0, 100.0),
    (111, '臺北市', '肉品類', 7232, 12, 99.83),
    (111, '臺北市', '蛋品類', 123, 4, 96.75),
    (111, '臺北市', '水產類', 730, 28, 96.16),
    (111, '臺北市', '蔬果類', 2139, 110, 94.86),
    (111, '臺北市', '添加物', 2, 0, 100.0),
    (112, '新北市', '肉品類', 8510, 21, 99.75),
    (112, '新北市', '蛋品類', 890, 7, 99.21),
    (112, '新北市', '水產類', 2749, 7, 99.75),
    (112, '新北市', '蔬果類', 6669, 42, 99.37),
    (112, '新北市', '添加物', 197, 0, 100.0),
    (112, '臺北市', '肉品類', 5775, 18, 99.69),
    (112, '臺北市', '蛋品類', 613, 2, 99.67),
    (112, '臺北市', '水產類', 690, 11, 98.41),
    (112, '臺北市', '蔬果類', 2829, 199, 92.97),
    (112, '臺北市', '添加物', 3, 0, 100.0),
    (113, '新北市', '肉品類', 14583, 6, 99.96),
    (113, '新北市', '蛋品類', 1385, 2, 99.86),
    (113, '新北市', '水產類', 4018, 0, 100.0),
    (113, '新北市', '蔬果類', 7683, 37, 99.52),
    (113, '新北市', '添加物', 578, 0, 100.0),
    (113, '臺北市', '肉品類', 9943, 20, 99.8),
    (113, '臺北市', '蛋品類', 766, 5, 99.35),
    (113, '臺北市', '水產類', 785, 15, 98.09),
    (113, '臺北市', '蔬果類', 3048, 202, 93.37),
    (113, '臺北市', '添加物', 28, 0, 100.0),
    (114, '新北市', '肉品類', 10949, 2, 99.98),
    (114, '新北市', '蛋品類', 740, 5, 99.32),
    (114, '新北市', '水產類', 2609, 0, 100.0),
    (114, '新北市', '蔬果類', 5615, 36, 99.36),
    (114, '新北市', '添加物', 87, 0, 100.0),
    (114, '臺北市', '肉品類', 8490, 13, 99.85),
    (114, '臺北市', '蛋品類', 611, 0, 100.0),
    (114, '臺北市', '水產類', 718, 11, 98.47),
    (114, '臺北市', '蔬果類', 2205, 157, 92.88),
    (114, '臺北市', '添加物', 7, 0, 100.0);

COMMIT;
