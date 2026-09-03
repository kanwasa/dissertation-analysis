
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select duplicates_removed
from "dissertation_analytics"."modern_dw"."quality_summary"
where duplicates_removed is null



  
  
      
    ) dbt_internal_test