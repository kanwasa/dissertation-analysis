
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select full_timestamp
from "dissertation_analytics"."modern_dw"."fact_sales"
where full_timestamp is null



  
  
      
    ) dbt_internal_test