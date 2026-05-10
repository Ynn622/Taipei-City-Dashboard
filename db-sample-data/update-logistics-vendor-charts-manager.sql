-- Updates the food logistics vendor component to use district-count charts
-- instead of the map legend chart in the dashboard overview.

BEGIN;

UPDATE public.components
SET name = '食品物流業者'
WHERE index = 'food_safety_logistics_vendor';

UPDATE public.component_charts
SET color = '{#4A90E2,#D84C73,#30B68F,#F5B041,#8E63C7,#F2C94C,#7A8793,#2F7D6D,#C2573E,#1E88E5,#00A6A6,#AF4137}',
    types = '{DistrictChart,TreemapChart,BarChart}',
    unit = '家'
WHERE index = 'food_safety_logistics_vendor';

UPDATE public.query_charts
SET short_desc = '統計雙北食品物流業者行政區分布。',
    long_desc = '此組件彙整衛生福利部食品藥物管理署食品業者登錄資料，篩選業者分類為物流業的食品物流業者，統計雙北各行政區業者數量，並以行政區圖、矩形圖與橫向長條圖呈現分布。',
    map_config_ids = ARRAY[(SELECT id FROM public.component_maps WHERE "index" = 'food_safety_logistics_vendor')],
    map_filter = '{"mode":"byParam","byParam":{"xParam":"district"}}'::json,
    query_type = 'two_d',
    query_chart = 'SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_safety_logistics_vendor WHERE district != '''' GROUP BY district ORDER BY data DESC, x_axis',
    updated_at = NOW()
WHERE index = 'food_safety_logistics_vendor'
  AND city = 'metrotaipei';

UPDATE public.query_charts
SET short_desc = '統計臺北市食品物流業者行政區分布。',
    long_desc = '此組件彙整衛生福利部食品藥物管理署食品業者登錄資料，篩選業者分類為物流業的食品物流業者，統計臺北市各行政區業者數量，並以行政區圖、矩形圖與橫向長條圖呈現分布。',
    map_config_ids = ARRAY[(SELECT id FROM public.component_maps WHERE "index" = 'food_safety_logistics_vendor')],
    map_filter = '{"mode":"byParam","byParam":{"xParam":"district"}}'::json,
    query_type = 'two_d',
    query_chart = 'SELECT district AS x_axis, COUNT(*)::int AS data FROM public.food_safety_logistics_vendor WHERE city = ''臺北市'' AND district != '''' GROUP BY district ORDER BY data DESC, x_axis',
    updated_at = NOW()
WHERE index = 'food_safety_logistics_vendor'
  AND city = 'taipei';

COMMIT;
