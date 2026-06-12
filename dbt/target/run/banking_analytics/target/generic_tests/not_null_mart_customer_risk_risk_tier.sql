
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select risk_tier
from "dev"."analytics"."mart_customer_risk"
where risk_tier is null



  
  
      
    ) dbt_internal_test