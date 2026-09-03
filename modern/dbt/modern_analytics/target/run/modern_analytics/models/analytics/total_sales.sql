
  create view "dissertation_analytics"."modern_dw"."total_sales__dbt_tmp"
    
    
  as (
    -- total_sales.sql
select
    sum(sales_amount) as total_sales
from "dissertation_analytics"."modern_dw"."fact_sales"
  );