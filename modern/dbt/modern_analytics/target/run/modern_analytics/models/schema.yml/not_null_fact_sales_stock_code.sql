
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select stock_code
from "dissertation_analytics"."modern_dw"."fact_sales"
where stock_code is null



  
  
      
    ) dbt_internal_test