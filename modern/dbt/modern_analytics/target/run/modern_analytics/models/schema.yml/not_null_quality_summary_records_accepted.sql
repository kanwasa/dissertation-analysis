
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select records_accepted
from "dissertation_analytics"."modern_dw"."quality_summary"
where records_accepted is null



  
  
      
    ) dbt_internal_test