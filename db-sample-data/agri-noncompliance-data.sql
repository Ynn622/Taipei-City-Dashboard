-- ════════════════════════════════════════════════════════════════════════════
-- 目標：postgres-data / dashboard
-- 指令：docker exec -i postgres-data psql -U postgres -d dashboard < agri-noncompliance-data.sql
-- ════════════════════════════════════════════════════════════════════════════

BEGIN;

-- ── 1. 建立資料表 ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.agri_sales_resume_noncompliance (
    sample_month       date,
    total_count        int,
    noncompliant_count int,
    noncompliance_rate float
);

-- ── 2. 寫入樣本資料（真實 API 計算值，DAG 執行後自動以完整值覆蓋）─────────
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
