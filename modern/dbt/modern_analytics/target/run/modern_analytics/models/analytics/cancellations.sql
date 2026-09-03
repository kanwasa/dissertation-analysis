
  create view "dissertation_analytics"."modern_dw"."cancellations__dbt_tmp"
    
    
  as (
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

from "dissertation_analytics"."modern_dw"."fact_sales"
  );