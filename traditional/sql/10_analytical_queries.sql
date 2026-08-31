-- ============================================================
-- TRADITIONAL PIPELINE: FIXED ANALYTICAL OUTPUTS
-- ============================================================


-- ============================================================
-- 1. Total Sales
-- Net sales across all accepted records.
-- Cancellation records therefore reduce total sales.
-- ============================================================

SELECT
    SUM(sales_amount) AS total_sales
FROM traditional_dw.fact_sales;


-- ============================================================
-- 2. Sales by Country
-- ============================================================

SELECT
    c.country_name,
    SUM(f.sales_amount) AS total_sales
FROM traditional_dw.fact_sales AS f
JOIN traditional_dw.dim_country AS c
    ON f.country_key = c.country_key
GROUP BY
    c.country_name
ORDER BY
    total_sales DESC;


-- ============================================================
-- 3. Average Invoice Value
-- First calculate each invoice total, then average
-- those invoice totals.
-- ============================================================

WITH invoice_totals AS (
    SELECT
        invoice_no,
        SUM(sales_amount) AS invoice_total
    FROM traditional_dw.fact_sales
    GROUP BY
        invoice_no
)
SELECT
    AVG(invoice_total) AS average_invoice_value
FROM invoice_totals;


-- ============================================================
-- 4. Unique Customer Count
-- Missing customers are excluded from this metric.
-- ============================================================

SELECT
    COUNT(DISTINCT customer_key) AS unique_customer_count
FROM traditional_dw.fact_sales
WHERE customer_key IS NOT NULL;


-- ============================================================
-- 5. Top-Performing Products
-- Top 10 products ranked by net sales amount.
-- ============================================================

SELECT
    p.stock_code,
    p.description,
    SUM(f.sales_amount) AS total_sales
FROM traditional_dw.fact_sales AS f
JOIN traditional_dw.dim_product AS p
    ON f.product_key = p.product_key
GROUP BY
    p.stock_code,
    p.description
ORDER BY
    total_sales DESC
LIMIT 10;


-- ============================================================
-- 6. Cancellation Count and Rate
-- Rate = cancellation rows / accepted fact rows * 100.
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE is_cancellation
    ) AS cancellation_count,

    ROUND(
        (
            100.0
            * COUNT(*) FILTER (WHERE is_cancellation)
            / NULLIF(COUNT(*), 0)
        ),
        4
    ) AS cancellation_rate_percent
FROM traditional_dw.fact_sales;


-- ============================================================
-- 7. Data-Quality Summary
-- recent pipeline run
-- ============================================================
SELECT
    workload_size,
    records_input,
    records_accepted,
    records_rejected,
    duplicates_removed,
    missing_customer_count,
    missing_description_count,
    cancellation_count
FROM traditional_dw.pipeline_run_audit
ORDER BY run_id DESC
LIMIT 1;