
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        risk_tier as value_field,
        count(*) as n_records

    from "dev"."analytics"."mart_customer_risk"
    group by risk_tier

)

select *
from all_values
where value_field not in (
    'Low Risk','Medium Risk','High Risk'
)



  
  
      
    ) dbt_internal_test