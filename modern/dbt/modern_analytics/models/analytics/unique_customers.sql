-- unique_customers.sql
select
    count(distinct customer_id) as unique_customer_count
from {{ ref('fact_sales') }}
where customer_id is not null