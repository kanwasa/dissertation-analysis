-- dim_product.sql

select distinct on (stock_code)
    stock_code,
    description
from "dissertation_analytics"."modern_dw"."int_accepted_records"
order by stock_code