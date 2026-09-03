
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    stock_code as unique_field,
    count(*) as n_records

from "dissertation_analytics"."modern_dw"."dim_product"
where stock_code is not null
group by stock_code
having count(*) > 1



  
  
      
    ) dbt_internal_test