-- dim_date.sql

select distinct
    invoice_date as full_timestamp,
    cast(invoice_date as date) as calendar_date,
    extract(year from invoice_date)::integer as year,
    extract(month from invoice_date)::integer as month,
    extract(day from invoice_date)::integer as day,
    extract(hour from invoice_date)::integer as hour
from {{ ref('int_accepted_records') }}