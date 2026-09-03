select
    f.stock_code,
    p.description,
    sum(f.sales_amount) as total_sales

from "dissertation_analytics"."modern_dw"."fact_sales" f

left join "dissertation_analytics"."modern_dw"."dim_product" p
    on f.stock_code = p.stock_code

group by
    f.stock_code,
    p.description

order by total_sales desc

limit 10