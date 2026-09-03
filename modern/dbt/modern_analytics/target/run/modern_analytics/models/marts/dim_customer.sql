
  
    

  create  table "dissertation_analytics"."modern_dw"."dim_customer__dbt_tmp"
  
  
    as
  
  (
    -- dim_customer.sql

select distinct
    customer_id
from "dissertation_analytics"."modern_dw"."int_accepted_records"
where customer_id is not null
  );
  