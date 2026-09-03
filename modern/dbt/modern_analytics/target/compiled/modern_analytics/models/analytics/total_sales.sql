-- total_sales.sql
select
    sum(sales_amount) as total_sales
from "dissertation_analytics"."modern_dw"."fact_sales"