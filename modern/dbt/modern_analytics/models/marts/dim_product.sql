-- dim_product.sql

select distinct on (stock_code)
    stock_code,
    description
from {{ ref('int_accepted_records') }}
order by stock_code