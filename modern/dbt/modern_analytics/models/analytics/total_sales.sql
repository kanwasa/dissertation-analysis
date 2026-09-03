-- total_sales.sql
select
    sum(sales_amount) as total_sales
from {{ ref('fact_sales') }}