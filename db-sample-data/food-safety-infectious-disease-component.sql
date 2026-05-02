BEGIN;

INSERT INTO public.components ("index", name)
SELECT 'cdc_infectious_disease', '腹瀉就診數量統計'
WHERE NOT EXISTS (
  SELECT 1 FROM public.components WHERE "index" = 'cdc_infectious_disease'
);

UPDATE public.components
SET name = '腹瀉就診數量統計'
WHERE "index" = 'cdc_infectious_disease';

INSERT INTO public.component_charts ("index", color, types, unit)
SELECT
  'cdc_infectious_disease',
  ARRAY['#4CB495', '#F5C860', '#ED6A45'],
  ARRAY['ColumnChart'],
  '人次'
WHERE NOT EXISTS (
  SELECT 1 FROM public.component_charts WHERE "index" = 'cdc_infectious_disease'
);

UPDATE public.component_charts
SET
  color = ARRAY['#4CB495', '#F5C860', '#ED6A45'],
  types = ARRAY['ColumnChart'],
  unit = '人次'
WHERE "index" = 'cdc_infectious_disease';

DO $$
DECLARE
  v_component_id integer;
  v_history_config json := '{"range":["max"],"color":["#4CB495","#F5C860","#ED6A45"],"unit":"人次"}'::json;
  v_taipei_query text := $sql$
    WITH latest_weeks AS (
      SELECT DISTINCT data_time
      FROM public.cdc_infectious_disease
      WHERE county = '臺北市'
      ORDER BY data_time DESC
      LIMIT 12
    ),
    weeks AS (
      SELECT data_time
      FROM latest_weeks
      ORDER BY data_time
    ),
    visit_types(visit_type, sort_order) AS (
      VALUES ('門診', 1), ('住院', 2), ('急診', 3)
    )
    SELECT
      TO_CHAR(w.data_time, 'YYYY-MM-DD') AS x_axis,
      v.visit_type AS y_axis,
      COALESCE(SUM(d.patient_visit), 0)::int AS data
    FROM weeks w
    CROSS JOIN visit_types v
    LEFT JOIN public.cdc_infectious_disease d
      ON d.data_time = w.data_time
     AND d.visit_type = v.visit_type
     AND d.county = '臺北市'
    GROUP BY w.data_time, v.visit_type, v.sort_order
    ORDER BY w.data_time, v.sort_order
  $sql$;
  v_metrotaipei_query text := $sql$
    WITH latest_weeks AS (
      SELECT DISTINCT data_time
      FROM public.cdc_infectious_disease
      WHERE county IN ('臺北市', '新北市')
      ORDER BY data_time DESC
      LIMIT 12
    ),
    weeks AS (
      SELECT data_time
      FROM latest_weeks
      ORDER BY data_time
    ),
    visit_types(visit_type, sort_order) AS (
      VALUES ('門診', 1), ('住院', 2), ('急診', 3)
    )
    SELECT
      TO_CHAR(w.data_time, 'YYYY-MM-DD') AS x_axis,
      v.visit_type AS y_axis,
      COALESCE(SUM(d.patient_visit), 0)::int AS data
    FROM weeks w
    CROSS JOIN visit_types v
    LEFT JOIN public.cdc_infectious_disease d
      ON d.data_time = w.data_time
     AND d.visit_type = v.visit_type
     AND d.county IN ('臺北市', '新北市')
    GROUP BY w.data_time, v.visit_type, v.sort_order
    ORDER BY w.data_time, v.sort_order
  $sql$;
  v_taipei_history_query text := $sql$
    WITH
    visit_types(visit_type, sort_order) AS (
      VALUES ('門診', 1), ('住院', 2), ('急診', 3)
    )
    SELECT
      MAKE_DATE(d.year, 1, 1)::timestamp AS x_axis,
      v.visit_type AS y_axis,
      SUM(d.patient_visit)::float AS data
    FROM public.cdc_infectious_disease d
    JOIN visit_types v ON d.visit_type = v.visit_type
    WHERE d.county = '臺北市'
      AND d.year BETWEEN 2016 AND 2026
    GROUP BY d.year, v.visit_type, v.sort_order
    ORDER BY d.year, v.sort_order
  $sql$;
  v_metrotaipei_history_query text := $sql$
    WITH
    visit_types(visit_type, sort_order) AS (
      VALUES ('門診', 1), ('住院', 2), ('急診', 3)
    )
    SELECT
      MAKE_DATE(d.year, 1, 1)::timestamp AS x_axis,
      v.visit_type AS y_axis,
      SUM(d.patient_visit)::float AS data
    FROM public.cdc_infectious_disease d
    JOIN visit_types v ON d.visit_type = v.visit_type
    WHERE d.county IN ('臺北市', '新北市')
      AND d.year BETWEEN 2016 AND 2026
    GROUP BY d.year, v.visit_type, v.sort_order
    ORDER BY d.year, v.sort_order
  $sql$;
BEGIN
  SELECT id INTO v_component_id
  FROM public.components
  WHERE "index" = 'cdc_infectious_disease';

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
    'cdc_infectious_disease',
    v_history_config,
    ARRAY[]::integer[],
    '{}'::json,
    'static',
    NULL,
    1,
    'week',
    '衛生福利部疾病管制署',
    '顯示臺北市近 12 週腹瀉門診、住院及急診就診人次。',
    '此組件彙整 CDC 腹瀉健保門診及住院就診人次統計與急性腹瀉急診傳染病監測統計；資料篩選 2016 至 2026 年，並以 ISO week 週一日期作為週資料時間。主圖顯示近 12 週，歷史圖以年份加總呈現。',
    '可用於觀察食安健康相關腸胃道症狀近期週變化與年度趨勢，輔助公共衛生監測與疫情風險溝通。',
    ARRAY[
      'https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv',
      'https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv'
    ],
    ARRAY['doit'],
    NOW(),
    NOW(),
    'three_d',
    v_taipei_query,
    v_taipei_history_query,
    'taipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts
    WHERE "index" = 'cdc_infectious_disease'
      AND city = 'taipei'
  );

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
    'cdc_infectious_disease',
    v_history_config,
    ARRAY[]::integer[],
    '{}'::json,
    'static',
    NULL,
    1,
    'week',
    '衛生福利部疾病管制署',
    '顯示雙北近 12 週腹瀉門診、住院及急診就診人次。',
    '此組件彙整 CDC 腹瀉健保門診及住院就診人次統計與急性腹瀉急診傳染病監測統計；資料篩選 2016 至 2026 年，並以 ISO week 週一日期作為週資料時間。雙北版本聚合臺北市與新北市，主圖顯示近 12 週，歷史圖以年份加總呈現。',
    '可用於觀察雙北食安健康相關腸胃道症狀近期週變化與年度趨勢，輔助公共衛生監測、疫情風險溝通與跨區比較。',
    ARRAY[
      'https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv',
      'https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv'
    ],
    ARRAY['doit'],
    NOW(),
    NOW(),
    'three_d',
    v_metrotaipei_query,
    v_metrotaipei_history_query,
    'metrotaipei'
  WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts
    WHERE "index" = 'cdc_infectious_disease'
      AND city = 'metrotaipei'
  );

  UPDATE public.query_charts
  SET
    history_config = v_history_config,
    map_config_ids = ARRAY[]::integer[],
    map_filter = '{}'::json,
    time_from = 'static',
    update_freq = 1,
    update_freq_unit = 'week',
    source = '衛生福利部疾病管制署',
    short_desc = '顯示臺北市近 12 週腹瀉門診、住院及急診就診人次。',
    long_desc = '此組件彙整 CDC 腹瀉健保門診及住院就診人次統計與急性腹瀉急診傳染病監測統計；資料篩選 2016 至 2026 年，並以 ISO week 週一日期作為週資料時間。主圖顯示近 12 週，歷史圖以年份加總呈現。',
    use_case = '可用於觀察食安健康相關腸胃道症狀近期週變化與年度趨勢，輔助公共衛生監測與疫情風險溝通。',
    links = ARRAY[
      'https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv',
      'https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv'
    ],
    contributors = ARRAY['doit'],
    updated_at = NOW(),
    query_type = 'three_d',
    query_chart = v_taipei_query,
    query_history = v_taipei_history_query
  WHERE "index" = 'cdc_infectious_disease'
    AND city = 'taipei';

  UPDATE public.query_charts
  SET
    history_config = v_history_config,
    map_config_ids = ARRAY[]::integer[],
    map_filter = '{}'::json,
    time_from = 'static',
    update_freq = 1,
    update_freq_unit = 'week',
    source = '衛生福利部疾病管制署',
    short_desc = '顯示雙北近 12 週腹瀉門診、住院及急診就診人次。',
    long_desc = '此組件彙整 CDC 腹瀉健保門診及住院就診人次統計與急性腹瀉急診傳染病監測統計；資料篩選 2016 至 2026 年，並以 ISO week 週一日期作為週資料時間。雙北版本聚合臺北市與新北市，主圖顯示近 12 週，歷史圖以年份加總呈現。',
    use_case = '可用於觀察雙北食安健康相關腸胃道症狀近期週變化與年度趨勢，輔助公共衛生監測、疫情風險溝通與跨區比較。',
    links = ARRAY[
      'https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv',
      'https://od.cdc.gov.tw/eic/RODS_AcuteDiarrhea.csv'
    ],
    contributors = ARRAY['doit'],
    updated_at = NOW(),
    query_type = 'three_d',
    query_chart = v_metrotaipei_query,
    query_history = v_metrotaipei_history_query
  WHERE "index" = 'cdc_infectious_disease'
    AND city = 'metrotaipei';

  UPDATE public.dashboards
  SET
    components = CASE
      WHEN components IS NULL THEN ARRAY[v_component_id]
      WHEN v_component_id = ANY(components) THEN components
      ELSE components || v_component_id
    END,
    updated_at = NOW()
  WHERE "index" IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei');
END $$;

COMMIT;
