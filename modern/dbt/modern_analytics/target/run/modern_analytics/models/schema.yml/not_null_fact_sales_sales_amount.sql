
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sales_amount
from "dissertation_analytics"."modern_dw"."fact_sales"
where sales_amount is null



  
  
      
    ) dbt_internal_test