-- Updates the public market component to remove the map legend chart and use
-- stall-type charts in the dashboard overview.

BEGIN;

UPDATE public.component_charts
SET color = '{#30B68F,#F5B041,#4A90E2,#D84C73,#8E63C7,#F2C94C,#7A8793,#C6A15B}',
    types = '{DonutChart,TreemapChart,BarChart}',
    unit = '攤'
WHERE index = 'food_safety_market';

UPDATE public.dashboards
SET components = array_remove(components, 307),
    updated_at = NOW()
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei')
  AND components IS NOT NULL;

UPDATE public.query_charts
SET short_desc = '顯示雙北公有市場分布與攤位類型統計。',
    long_desc = '顯示臺北市各區公有零售市(商)場與新北市公有市場名冊之空間分布，並以圓餅圖、矩形圖與橫向長條圖呈現公有市場攤位類型彙總。臺北資料包含市場名稱、行政區與各營業種類攤位數，新北資料包含市場名稱、行政區、地址、電話與市場型態；資料經批次地理編碼後轉為地圖點位，提供市場分布、攤位結構與食安巡檢、公共衛生資源配置的基礎圖資。',
    use_case = '可用於食安稽查排程、市場周邊公共衛生服務配置、跨區市場分布比較、攤位營業類型結構分析，以及與人口、交通、醫療或災防圖層套疊分析，協助掌握民生採買場域與健康風險管理的空間關係。',
    query_type = 'two_d',
    query_chart = $chart$WITH stall_summary AS (
    SELECT
        SUM(COALESCE(general_merchandise_stalls, 0) + COALESCE(flower_stalls, 0)) AS merch_flower,
        SUM(COALESCE(vegetable_stalls, 0) + COALESCE(fruit_stalls, 0)) AS produce,
        SUM(COALESCE(grain_stalls, 0) + COALESCE(grocery_stalls, 0)) AS grain_grocery,
        SUM(COALESCE(meat_stalls, 0) + COALESCE(poultry_stalls, 0)) AS meat_poultry,
        SUM(COALESCE(food_stalls, 0)) AS food,
        SUM(COALESCE(seafood_stalls, 0)) AS seafood,
        SUM(COALESCE(other_stalls, 0)) AS other,
        0::numeric AS vacant
    FROM public.food_safety_market_tpe
    UNION ALL
    SELECT
        SUM(COALESCE(general_merchandise_stalls, 0) + COALESCE(flower_stalls, 0)) AS merch_flower,
        SUM(COALESCE(produce_stalls, 0)) AS produce,
        SUM(COALESCE(grain_stalls, 0) + COALESCE(grocery_stalls, 0)) AS grain_grocery,
        SUM(COALESCE(meat_stalls, 0) + COALESCE(poultry_stalls, 0)) AS meat_poultry,
        SUM(COALESCE(food_stalls, 0)) AS food,
        SUM(COALESCE(seafood_stalls, 0)) AS seafood,
        SUM(COALESCE(other_stalls, 0)) AS other,
        SUM(COALESCE(vacant_stalls, 0)) AS vacant
    FROM public.food_safety_market_ntpe
), totals AS (
    SELECT
        SUM(merch_flower) AS merch_flower,
        SUM(produce) AS produce,
        SUM(grain_grocery) AS grain_grocery,
        SUM(meat_poultry) AS meat_poultry,
        SUM(food) AS food,
        SUM(seafood) AS seafood,
        SUM(other) AS other,
        SUM(vacant) AS vacant
    FROM stall_summary
)
SELECT x_axis, data::int AS data
FROM totals
CROSS JOIN LATERAL (
    VALUES
        (1, '百貨花卉', merch_flower),
        (2, '蔬果', produce),
        (3, '糧食雜貨', grain_grocery),
        (4, '肉禽', meat_poultry),
        (5, '飲食', food),
        (6, '水產', seafood),
        (7, '其他', other),
        (8, '空攤', vacant)
) AS chart(sort, x_axis, data)
ORDER BY sort$chart$,
    updated_at = NOW()
WHERE index = 'food_safety_market'
  AND city = 'metrotaipei';

UPDATE public.query_charts
SET short_desc = '顯示臺北市公有市場分布與攤位類型統計。',
    long_desc = '顯示臺北市各區公有零售市(商)場之空間分布，並以圓餅圖、矩形圖與橫向長條圖呈現攤位類型彙總；資料包含市場名稱、行政區與各營業種類攤位數，並經批次地理編碼後轉為地圖點位，提供市場分布、攤位結構與食安巡檢、公共衛生資源配置的基礎圖資。',
    use_case = '可用於食安稽查排程、市場周邊公共衛生服務配置、行政區市場分布比較、攤位營業類型結構分析，以及與人口、交通、醫療或災防圖層套疊分析。',
    query_type = 'two_d',
    query_chart = $chart$WITH totals AS (
    SELECT
        SUM(COALESCE(general_merchandise_stalls, 0) + COALESCE(flower_stalls, 0)) AS merch_flower,
        SUM(COALESCE(vegetable_stalls, 0) + COALESCE(fruit_stalls, 0)) AS produce,
        SUM(COALESCE(grain_stalls, 0) + COALESCE(grocery_stalls, 0)) AS grain_grocery,
        SUM(COALESCE(meat_stalls, 0) + COALESCE(poultry_stalls, 0)) AS meat_poultry,
        SUM(COALESCE(food_stalls, 0)) AS food,
        SUM(COALESCE(seafood_stalls, 0)) AS seafood,
        SUM(COALESCE(other_stalls, 0)) AS other
    FROM public.food_safety_market_tpe
)
SELECT x_axis, data::int AS data
FROM totals
CROSS JOIN LATERAL (
    VALUES
        (1, '百貨花卉', merch_flower),
        (2, '蔬果', produce),
        (3, '糧食雜貨', grain_grocery),
        (4, '肉禽', meat_poultry),
        (5, '飲食', food),
        (6, '水產', seafood),
        (7, '其他', other)
) AS chart(sort, x_axis, data)
ORDER BY sort$chart$,
    updated_at = NOW()
WHERE index = 'food_safety_market'
  AND city = 'taipei';

DELETE FROM public.query_charts
WHERE index = 'food_safety_market_stall_ratio';

DELETE FROM public.component_charts
WHERE index = 'food_safety_market_stall_ratio';

DELETE FROM public.components
WHERE index = 'food_safety_market_stall_ratio'
  AND NOT EXISTS (
    SELECT 1 FROM public.dashboards WHERE 307 = ANY(components)
  );

SELECT setval('public.components_id_seq', (SELECT COALESCE(MAX(id), 0) FROM public.components), true);

COMMIT;
