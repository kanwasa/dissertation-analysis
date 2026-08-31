TRUNCATE TABLE
    traditional_dw.fact_sales,
    traditional_dw.dim_customer,
    traditional_dw.dim_product,
    traditional_dw.dim_date,
    traditional_dw.dim_country,
	traditional_dw.pipeline_run_audit
RESTART IDENTITY
CASCADE;

SELECT COUNT(*)
FROM traditional_dw.fact_sales;