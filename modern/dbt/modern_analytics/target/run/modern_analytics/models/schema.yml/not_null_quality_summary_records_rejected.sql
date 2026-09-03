
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select records_rejected
from "dissertation_analytics"."modern_dw"."quality_summary"
where records_rejected is null



  
  
      
    ) dbt_internal_test