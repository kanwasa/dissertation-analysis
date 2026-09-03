
  create view "dissertation_analytics"."modern_dw"."average_invoice_value__dbt_tmp"
    
    
  as (
    -- average_invoice_value.sql
with invoice_totals as (

    select
        invoice_no,
        sum(sales_amount) as invoice_total
    from "dissertation_analytics"."modern_dw"."fact_sales"
    group by invoice_no

)

select
    avg(invoice_total) as average_invoice_value
from invoice_totals
  );