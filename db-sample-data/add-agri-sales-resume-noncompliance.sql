-- Agri Sales Resume Non-Compliance Rate Component Setup
-- Component ID: 506
-- Index: agri_sales_resume_noncompliance
-- Description: 農產品產銷履歷不合格率（按月統計，全台）

BEGIN;

-- ── 1. 建立資料表（postgres-data）────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.agri_sales_resume_noncompliance (
    sample_month       date,
    total_count        int,
    noncompliant_count int,
    noncompliance_rate float
);

-- ── 2. 在 Manager DB 登錄組件（postgres-manager）────────────────────────────
INSERT INTO public.components (id, "index", name)
VALUES (506, 'agri_sales_resume_noncompliance', '農產品產銷履歷不合格率')
ON CONFLICT (id) DO UPDATE SET
    "index" = EXCLUDED."index",
    name    = EXCLUDED.name;

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

-- ── 3. Query charts: taipei ───────────────────────────────────────────────────
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

-- ── 3b. Query charts: metrotaipei ────────────────────────────────────────────
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

-- ── 4. 掛入 Dashboard ────────────────────────────────────────────────────────
UPDATE public.dashboards
SET components = array_append(components, 506),
    updated_at = NOW()
WHERE index IN ('food_safety_health_tpe', 'food_safety_health_metrotaipei')
  AND NOT (506 = ANY(components));

-- ── 5. 樣本資料（源自 MOA API 單頁回應真實計算）─────────────────────────────
-- 資料來源：農業部農糧署 API 第一頁回應（共 ~1120 筆，Next: true 表示尚有更多頁）
-- 涵蓋期間：民國 114 年 7 月 ~ 12 月（2025-07 ~ 2025-12）
-- 不合格定義：InspectResult 非「合格」者（含「不合格」「標示合格/品質不合格」「品質合格/標示不合格」）
-- 不合格筆數為精確計數，總筆數為各月估算值；DAG 執行後自動以精確值覆蓋。
--
-- 各月不合格明細（已完整掃描 API 回應）：
--   2025-07：3 筆（1140703 不合格、1140724 標示合格、1140725 標示合格）
--   2025-08：3 筆（1140807 標示合格、1140811 品質合格×2）
--   2025-09：4 筆（1140902 不合格、1140903 不合格、1140917 品質合格、1140930 不合格）
--   2025-10：2 筆（1141021 標示合格、1141030 不合格）
--   2025-11：3 筆（1141120 標示合格、1141127 標示合格、1141128 品質合格）
--   2025-12：0 筆
DELETE FROM public.agri_sales_resume_noncompliance
WHERE sample_month BETWEEN '2025-07-01' AND '2025-12-01';

INSERT INTO public.agri_sales_resume_noncompliance
    (sample_month, total_count, noncompliant_count, noncompliance_rate)
VALUES
    ('2025-07-01', 330, 3, 0.91),
    ('2025-08-01', 220, 3, 1.36),
    ('2025-09-01', 200, 4, 2.00),
    ('2025-10-01', 200, 2, 1.00),
    ('2025-11-01', 130, 3, 2.31),
    ('2025-12-01',  50, 0, 0.00);

COMMIT;
