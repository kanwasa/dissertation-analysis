select *
from "dissertation_analytics"."modern_dw"."int_classified_records"
where rejection_reason is not null
  and duplicate_flag = false