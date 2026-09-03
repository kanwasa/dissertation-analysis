select *
from {{ ref('int_classified_records') }}
where duplicate_flag = true