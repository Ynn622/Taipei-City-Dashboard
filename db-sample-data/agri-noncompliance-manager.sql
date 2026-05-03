-- ════════════════════════════════════════════════════════════════════════════
-- 目標：postgres-manager / dashboardmanager
-- 指令：docker exec -i postgres-manager psql -U postgres -d dashboardmanager < agri-noncompliance-manager.sql
-- ════════════════════════════════════════════════════════════════════════════

BEGIN;

-- ── 1. 登錄組件 ───────────────────────────────────────────────────────────
INSERT INTO public.components (id, "index", name)
VALUES (506, 'agri_sales_resume_noncompliance', '產銷履歷合格率')
ON CONFLICT (id) DO UPDATE SET
    "index" = EXCLUDED."index",
    name    = EXCLUDED.name;

-- ── 2. 圖表設定 ──────────────────────────────────────────────────────────
INSERT INTO public.component_charts ("index", color, types, unit)
VALUES (
    'agri_sales_resume_noncompliance',
    ARRAY['#ED6A45'],
    ARRAY['TimelineSeparateChart'],
    '%'
)
ON CONFLICT ("index") DO UPDATE SET
    color = EXCLUDED.color,
    types = EXCLUDED.types,
    unit  = EXCLUDED.unit;

-- ── 3. Query charts ──────────────────────────────────────────────────────
INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
)
SELECT
    'agri_sales_resume_noncompliance',
    '{"range":["max"],"color":["#ED6A45"],"unit":"%"}'::json,
    ARRAY[]::integer[], '{}'::json, 'static', NULL, 1, 'week',
    '農業部農糧署',
    '顯示全台農產品產銷履歷抽驗之整體不合格率，以月份為單位呈現趨勢。',
    '此組件爬取農業部農糧署產銷履歷農產品抽驗結果，依 InspectResult 欄位判定合格與否（非「合格」均視為不合格，涵蓋品質不合格及標示不合格），按月份聚合計算不合格率並以折線圖呈現趨勢。',
    '可用於觀察全台農產品產銷履歷制度執行成效，輔助食安政策評估與農業輔導資源配置。',
    ARRAY['https://data.moa.gov.tw/api.aspx#operations-tag-%E7%94%A2%E9%8A%B7%E5%B1%A5%E6%AD%B7'],
    ARRAY['doit'], NOW(), NOW(), 'time',
    $chart$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $chart$,
    $hist$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $hist$,
    'taipei'
WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts
    WHERE "index" = 'agri_sales_resume_noncompliance' AND city = 'taipei'
);

UPDATE public.query_charts SET
    query_chart = $chart$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $chart$,
    query_history = $hist$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $hist$,
    links = ARRAY['https://data.moa.gov.tw/api.aspx#operations-tag-%E7%94%A2%E9%8A%B7%E5%B1%A5%E6%AD%B7']
WHERE "index" = 'agri_sales_resume_noncompliance' AND city = 'taipei';

-- ── 3b. Query charts: metrotaipei ─────────────────────────────────────────
INSERT INTO public.query_charts (
    "index", history_config, map_config_ids, map_filter, time_from, time_to,
    update_freq, update_freq_unit, source, short_desc, long_desc, use_case,
    links, contributors, created_at, updated_at, query_type, query_chart, query_history, city
)
SELECT
    'agri_sales_resume_noncompliance',
    '{"range":["max"],"color":["#ED6A45"],"unit":"%"}'::json,
    ARRAY[]::integer[], '{}'::json, 'static', NULL, 1, 'week',
    '農業部農糧署',
    '顯示全台農產品產銷履歷抽驗之整體不合格率，以月份為單位呈現趨勢。',
    '此組件爬取農業部農糧署產銷履歷農產品抽驗結果，依 InspectResult 欄位判定合格與否（非「合格」均視為不合格，涵蓋品質不合格及標示不合格），按月份聚合計算不合格率並以折線圖呈現趨勢。',
    '可用於觀察全台農產品產銷履歷制度執行成效，輔助食安政策評估與農業輔導資源配置。',
    ARRAY['https://data.moa.gov.tw/api.aspx#operations-tag-%E7%94%A2%E9%8A%B7%E5%B1%A5%E6%AD%B7'],
    ARRAY['doit'], NOW(), NOW(), 'time',
    $chart$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $chart$,
    $hist$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $hist$,
    'metrotaipei'
WHERE NOT EXISTS (
    SELECT 1 FROM public.query_charts
    WHERE "index" = 'agri_sales_resume_noncompliance' AND city = 'metrotaipei'
);

UPDATE public.query_charts SET
    query_chart = $chart$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $chart$,
    query_history = $hist$
SELECT
    sample_month::timestamp AS x_axis,
    '不合格率' AS y_axis,
    ROUND(noncompliance_rate::numeric, 2) AS data
FROM public.agri_sales_resume_noncompliance
ORDER BY sample_month
    $hist$,
    links = ARRAY['https://data.moa.gov.tw/api.aspx#operations-tag-%E7%94%A2%E9%8A%B7%E5%B1%A5%E6%AD%B7']
WHERE "index" = 'agri_sales_resume_noncompliance' AND city = 'metrotaipei';

-- ── 4. 掛入 Dashboard ────────────────────────────────────────────────────
UPDATE public.dashboards
SET components = array_append(components, 506),
    updated_at = NOW()
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei')
  AND NOT (506 = ANY(components));

COMMIT;
