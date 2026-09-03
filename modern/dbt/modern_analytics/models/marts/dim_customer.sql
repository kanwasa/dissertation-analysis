-- dim_customer.sql

select distinct
    customer_id
from {{ ref('int_accepted_records') }}
where customer_id is not null