select
    *,
    quantity * price as sales_amount
from "dissertation_analytics"."modern_dw"."int_classified_records"
where rejection_reason is null
  and duplicate_flag = false