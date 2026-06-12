
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select default_rate_pct
from "dev"."analytics"."mart_loan_performance"
where default_rate_pct is null



  
  
      
    ) dbt_internal_test