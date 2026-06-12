
    
    

with all_values as (

    select
        income_band as value_field,
        count(*) as n_records

    from "dev"."analytics"."mart_customer_risk"
    group by income_band

)

select *
from all_values
where value_field not in (
    'Low Income','Mid Income','High Income'
)


