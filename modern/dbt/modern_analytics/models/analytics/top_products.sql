select
    f.stock_code,
    p.description,
    sum(f.sales_amount) as total_sales

from {{ ref('fact_sales') }} f

left join {{ ref('dim_product') }} p
    on f.stock_code = p.stock_code

group by
    f.stock_code,
    p.description

order by total_sales desc

limit 10