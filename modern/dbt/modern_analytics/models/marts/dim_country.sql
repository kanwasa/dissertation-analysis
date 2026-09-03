-- dim_country.sql

select distinct
    country as country_name
from {{ ref('int_accepted_records') }}