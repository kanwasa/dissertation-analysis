-- cancellations.sql
select
    count(*) filter (
        where is_cancellation
    ) as cancellation_count,

    round(
        (
            100.0
            * count(*) filter (where is_cancellation)
            / nullif(count(*), 0)
        ),
        4
    ) as cancellation_rate_percent

from {{ ref('fact_sales') }}