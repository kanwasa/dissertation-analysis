with staged as (

    select *
    from "dissertation_analytics"."modern_dw"."stg_online_retail"

),

classified as (

    select
        invoice,
        stock_code,
        description,
        quantity,
        invoice_date,
        price,
        customer_id,
        country,

        is_cancellation,
        missing_customer_flag,
        missing_description_flag,

        row_number() over (
            partition by
                invoice,
                stock_code,
                description,
                quantity,
                invoice_date,
                price,
                customer_id,
                country
            order by invoice
        ) > 1 as duplicate_flag,

        case
            when invoice is null
                then 'Missing Invoice'

            when stock_code is null
                then 'Missing StockCode'

            when invoice_date is null
                then 'Invalid or missing InvoiceDate'

            when quantity is null
                then 'Invalid or missing Quantity'

            when price is null
                then 'Invalid or missing Price'

            when country is null
                then 'Missing Country'

            when quantity < 0
                 and not is_cancellation
                then 'Negative Quantity on non-cancellation'

            when price < 0
                then 'Negative Price'

            else null
        end as rejection_reason

    from staged

)

select *
from classified