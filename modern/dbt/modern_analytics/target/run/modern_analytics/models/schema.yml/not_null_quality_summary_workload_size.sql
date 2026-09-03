
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select workload_size
from "dissertation_analytics"."modern_dw"."quality_summary"
where workload_size is null



  
  
      
    ) dbt_internal_test