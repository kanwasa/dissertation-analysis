
  
    

  create  table "dissertation_analytics"."modern_dw"."quality_summary__dbt_tmp"
  
  
    as
  
  (
    


with counts as (

    select
        (select count(*) from "dissertation_analytics"."modern_raw"."online_retail_raw") as records_input,
        (select count(*) from "dissertation_analytics"."modern_dw"."int_accepted_records") as records_accepted,
        (select count(*) from "dissertation_analytics"."modern_dw"."int_rejected_records") as records_rejected,
        (select count(*) from "dissertation_analytics"."modern_dw"."int_duplicate_records") as duplicates_removed

),

quality_flags as (

    select
        sum(
            case when missing_customer_flag then 1 else 0 end
        ) as missing_customer_count,

        sum(
            case when missing_description_flag then 1 else 0 end
        ) as missing_description_count,

        sum(
            case when is_cancellation then 1 else 0 end
        ) as cancellation_count

    from "dissertation_analytics"."modern_dw"."int_accepted_records"

)

select
    counts.records_input as workload_size,
    counts.records_input,
    counts.records_accepted,
    counts.records_rejected,
    counts.duplicates_removed,
    quality_flags.missing_customer_count,
    quality_flags.missing_description_count,
    quality_flags.cancellation_count
from counts
cross join quality_flags
  );
  