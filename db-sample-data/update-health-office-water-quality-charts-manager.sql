-- Updates health office and water quality components to use analytical charts
-- instead of map legend charts in the dashboard overview.

BEGIN;

UPDATE public.components
SET name = '衛生監管機構'
WHERE index = 'food_safety_health_office';

UPDATE public.component_charts
SET color = '{#2F7D6D,#C2573E,#F2C94C}',
    types = '{DonutChart,TreemapChart,BarChart}',
    unit = '處'
WHERE index = 'food_safety_health_office';

UPDATE public.query_charts
SET short_desc = '顯示雙北衛生監管機構服務據點類型統計。',
    long_desc = '顯示臺北市政府衛生局、臺北市健康服務中心、新北市政府衛生局與新北市各區衛生所之空間分布，並以圓餅圖、矩形圖與橫向長條圖呈現各類型據點數量；包含名稱、行政區、地址、電話、服務時間或網站等資訊。臺北市點位優先使用臺北市門牌位置數值資料定位，新北市點位使用 OpenStreetMap 道路/地名定位。',
    query_type = 'two_d',
    query_chart = 'SELECT unnest(array[''衛生所'',''健康服務中心'',''衛生監管機構'']) as x_axis, unnest(array[29,12,2]) as data',
    updated_at = NOW()
WHERE index = 'food_safety_health_office'
  AND city = 'metrotaipei';

UPDATE public.query_charts
SET short_desc = '顯示臺北市衛生監管機構與健康服務中心類型統計。',
    long_desc = '顯示臺北市政府衛生局與各區健康服務中心之空間分布，並以圓餅圖、矩形圖與橫向長條圖呈現各類型據點數量；包含名稱、行政區、地址、電話與網站等資訊。點位優先使用臺北市門牌位置數值資料定位。',
    query_type = 'two_d',
    query_chart = 'SELECT unnest(array[''健康服務中心'',''衛生監管機構'']) as x_axis, unnest(array[12,1]) as data',
    updated_at = NOW()
WHERE index = 'food_safety_health_office'
  AND city = 'taipei';

UPDATE public.components
SET name = '淨水場水質濁度'
WHERE index = 'water_quality';

UPDATE public.component_charts
SET color = '{#2F7D6D,#30B68F,#1E88E5,#F5B041,#D84C73}',
    types = '{BarChart}',
    unit = 'NTU'
WHERE index = 'water_quality';

UPDATE public.query_charts
SET short_desc = '顯示雙北淨水場水質濁度比較。',
    long_desc = '顯示臺北自來水淨水場清水水質年度統計，以及臺灣自來水公司平均水質中關鍵字為新北市的淨水場最新測值；總覽以橫向長條圖比較各淨水場濁度(NTU)，並在地圖點位中提供 pH、濁度、自由有效餘氯、總硬度、總溶解固體量與大腸桿菌群等欄位。',
    query_type = 'two_d',
    query_chart = 'SELECT unnest(array[''林莊淨水場'',''員山淨水場'',''雙溪淨水場'',''老梅淨水場'',''貢寮淨水場'',''陽明淨水場'',''坪林淨水場'',''板新淨水場'',''長興淨水場'',''公館淨水場'',''直潭淨水場'']) as x_axis, unnest(array[0.55,0.5,0.48,0.45,0.4,0.32,0.25,0.2,0.2,0.1,0.1]) as data',
    updated_at = NOW()
WHERE index = 'water_quality'
  AND city = 'metrotaipei';

UPDATE public.query_charts
SET short_desc = '顯示臺北市淨水場水質濁度比較。',
    long_desc = '顯示臺北自來水淨水場清水水質年度統計；總覽以橫向長條圖比較各淨水場濁度(NTU)，並在地圖點位中提供 pH、濁度、自由有效餘氯、總硬度、總溶解固體量與大腸桿菌群等欄位。',
    query_type = 'two_d',
    query_chart = 'SELECT unnest(array[''雙溪淨水場'',''陽明淨水場'',''長興淨水場'',''公館淨水場'',''直潭淨水場'']) as x_axis, unnest(array[0.48,0.32,0.2,0.1,0.1]) as data',
    updated_at = NOW()
WHERE index = 'water_quality'
  AND city = 'taipei';

COMMIT;
