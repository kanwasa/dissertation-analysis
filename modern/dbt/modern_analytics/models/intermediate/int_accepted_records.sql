select
    *,
    quantity * price as sales_amount
from {{ ref('int_classified_records') }}
where rejection_reason is null
  and duplicate_flag = false