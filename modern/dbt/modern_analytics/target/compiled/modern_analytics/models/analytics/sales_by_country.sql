-- sales_by_country.sql
select
    country_name,
    sum(sales_amount) as total_sales
from "dissertation_analytics"."modern_dw"."fact_sales"
group by country_name
order by total_sales desc