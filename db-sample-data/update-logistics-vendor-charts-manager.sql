-- Updates the food logistics vendor component to use district-count charts
-- instead of the map legend chart in the dashboard overview.

BEGIN;

UPDATE public.component_charts
SET color = '{#4A90E2,#D84C73,#30B68F,#F5B041,#8E63C7,#F2C94C,#7A8793,#2F7D6D,#C2573E,#1E88E5,#00A6A6,#AF4137}',
    types = '{DonutChart,TreemapChart,BarChart}',
    unit = '家'
WHERE index = 'food_safety_logistics_vendor';

UPDATE public.query_charts
SET short_desc = '顯示雙北食品物流業者行政區分布。',
    long_desc = '顯示 FDA 食品業者登錄中分類為物流業的雙北業者行政區分布，並以圓餅圖、矩形圖與橫向長條圖呈現各行政區業者數量。資料由縣市列表端點以 tp=6 抓取，因來源未提供業者經緯度，臺北市地圖先以臺北市門牌位置數值資料定位，未成功者再使用地址轉座標與 OpenStreetMap 道路/地名定位，最後才以行政區中心點加微小偏移顯示每筆業者，並提供業者名稱、登錄字號、地址等欄位。',
    query_type = 'two_d',
    query_chart = 'SELECT unnest(array[''新莊區'',''五股區'',''中山區'',''汐止區'',''中和區'',''樹林區'',''林口區'',''松山區'',''三重區'',''內湖區'',''萬華區'',''板橋區'',''士林區'',''新店區'',''土城區'',''八里區'',''南港區'',''大安區'',''信義區'',''北投區'',''三峽區'',''瑞芳區'',''鶯歌區'',''中正區'',''蘆洲區'',''泰山區'',''大同區'',''淡水區'',''文山區'',''永和區'',''三芝區'',''深坑區'']) as x_axis, unnest(array[63,60,53,50,48,36,34,31,29,29,29,28,27,25,24,22,21,19,14,13,11,11,10,9,9,8,7,6,4,3,1,1]) as data',
    updated_at = NOW()
WHERE index = 'food_safety_logistics_vendor'
  AND city = 'metrotaipei';

UPDATE public.query_charts
SET short_desc = '顯示臺北市食品物流業者行政區分布。',
    long_desc = '顯示 FDA 食品業者登錄中分類為物流業的臺北市業者行政區分布，並以圓餅圖、矩形圖與橫向長條圖呈現各行政區業者數量。資料由縣市列表端點以 tp=6 抓取，因來源未提供業者經緯度，地圖先以臺北市門牌位置數值資料定位，未成功者再使用地址轉座標與 OpenStreetMap 道路/地名定位，最後才以行政區中心點加微小偏移顯示每筆業者，並提供業者名稱、登錄字號、地址等欄位。',
    query_type = 'two_d',
    query_chart = 'SELECT unnest(array[''中山區'',''松山區'',''內湖區'',''萬華區'',''士林區'',''南港區'',''大安區'',''信義區'',''北投區'',''中正區'',''大同區'',''文山區'']) as x_axis, unnest(array[53,31,29,29,27,21,19,14,13,9,7,4]) as data',
    updated_at = NOW()
WHERE index = 'food_safety_logistics_vendor'
  AND city = 'taipei';

COMMIT;
