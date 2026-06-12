
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select contract_type
from "dev"."analytics"."mart_application_funnel"
where contract_type is null



  
  
      
    ) dbt_internal_test