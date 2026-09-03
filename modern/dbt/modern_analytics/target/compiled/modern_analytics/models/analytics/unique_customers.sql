-- unique_customers.sql
select
    count(distinct customer_id) as unique_customer_count
from "dissertation_analytics"."modern_dw"."fact_sales"
where customer_id is not null