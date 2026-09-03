select
    invoice as invoice_no,
    customer_id,
    stock_code,
    invoice_date as full_timestamp,
    country as country_name,

    quantity,
    price as unit_price,
    sales_amount,

    is_cancellation,
    missing_customer_flag,
    missing_description_flag

from "dissertation_analytics"."modern_dw"."int_accepted_records"