
  
    

  create  table "dissertation_analytics"."modern_dw"."dim_country__dbt_tmp"
  
  
    as
  
  (
    -- dim_country.sql

select distinct
    country as country_name
from "dissertation_analytics"."modern_dw"."int_accepted_records"
  );
  