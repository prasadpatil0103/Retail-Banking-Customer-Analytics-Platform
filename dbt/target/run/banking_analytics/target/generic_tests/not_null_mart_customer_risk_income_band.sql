
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select income_band
from "dev"."analytics"."mart_customer_risk"
where income_band is null



  
  
      
    ) dbt_internal_test