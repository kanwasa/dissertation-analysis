
  create view "dissertation_analytics"."modern_dw"."stg_online_retail__dbt_tmp"
    
    
  as (
    with source as (

    select *
    from "dissertation_analytics"."modern_raw"."online_retail_raw"

),

staged as (

    select
        invoice,
        stock_code,
        description,

        case
            when trim(quantity) ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'
            then trim(quantity)::numeric
            else null
        end as quantity,

        case
            when trim(price) ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'
            then trim(price)::numeric
            else null
        end as price,
        

        case
            -- DD-MM-YYYY HH:MI
            when trim(invoice_date)
                ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}$'
            then to_timestamp(
                trim(invoice_date),
                'DD-MM-YYYY HH24:MI'
            )

            -- YYYY-MM-DD HH:MI:SS
            when trim(invoice_date)
                ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
            then to_timestamp(
                trim(invoice_date),
                'YYYY-MM-DD HH24:MI:SS'
            )

            else null
        end as invoice_date,

        customer_id,
        country,

        case
            when invoice like 'C%' then true
            else false
        end as is_cancellation,

        case
            when customer_id is null then true
            else false
        end as missing_customer_flag,

        case
            when description is null then true
            else false
        end as missing_description_flag

    from source

)

select *
from staged
  );