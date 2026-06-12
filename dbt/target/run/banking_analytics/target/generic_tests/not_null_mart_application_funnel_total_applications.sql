
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_applications
from "dev"."analytics"."mart_application_funnel"
where total_applications is null



  
  
      
    ) dbt_internal_test