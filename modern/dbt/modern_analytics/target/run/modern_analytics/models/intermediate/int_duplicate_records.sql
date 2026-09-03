
  create view "dissertation_analytics"."modern_dw"."int_duplicate_records__dbt_tmp"
    
    
  as (
    select *
from "dissertation_analytics"."modern_dw"."int_classified_records"
where duplicate_flag = true
  );