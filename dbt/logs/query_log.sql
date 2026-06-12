-- created_at: 2026-06-09T23:46:26.817762+00:00
-- finished_at: 2026-06-09T23:46:26.902239+00:00
-- elapsed: 84ms
-- outcome: success
-- dialect: redshift
-- node_id: not available
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "connection_name": "", "dbt_version": "2.0.0", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select distinct nspname from pg_namespace;
-- created_at: 2026-06-09T23:46:26.928957+00:00
-- finished_at: 2026-06-09T23:46:27.018447+00:00
-- elapsed: 89ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.stg_applications
-- query_id: not available
-- desc: get_relation > list_relations call
select
    table_catalog as database,
    table_name as name,
    table_schema as schema,
    'table' as type
from information_schema.tables
where table_schema ilike 'analytics'
and table_type = 'BASE TABLE'
union all
select
    table_catalog as database,
    table_name as name,
    table_schema as schema,
    case
    when view_definition ilike '%create materialized view%'
        then 'materialized_view'
    else 'view'
    end as type
from information_schema.views
where table_schema ilike 'analytics';
-- created_at: 2026-06-09T23:46:27.235618+00:00
-- finished_at: 2026-06-09T23:46:27.335158+00:00
-- elapsed: 99ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.stg_applications_dim
-- query_id: not available
-- desc: get_relation > list_relations call
select
    table_catalog as database,
    table_name as name,
    table_schema as schema,
    'table' as type
from information_schema.tables
where table_schema ilike 'analytics'
and table_type = 'BASE TABLE'
union all
select
    table_catalog as database,
    table_name as name,
    table_schema as schema,
    case
    when view_definition ilike '%create materialized view%'
        then 'materialized_view'
    else 'view'
    end as type
from information_schema.views
where table_schema ilike 'analytics';
-- created_at: 2026-06-09T23:46:27.021233+00:00
-- finished_at: 2026-06-09T23:46:27.683798+00:00
-- elapsed: 662ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.stg_applications
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.stg_applications", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
create or replace view "dev"."analytics"."stg_applications" as (
    with source as (
    select * from "dev"."public"."fact_loans"
),

renamed as (
    select
        customer_id,
        contract_type,
        credit_amount,
        annuity_amount,
        income_total,
        goods_price,
        debt_to_income_ratio,
        credit_income_ratio,
        ext_source_mean,
        age_years,
        employment_years,
        region_rating,
        income_type,
        education_type,
        target,
        ingestion_timestamp
    from source
)

select * from renamed
  ) ;
-- created_at: 2026-06-09T23:46:27.551848+00:00
-- finished_at: 2026-06-09T23:46:27.684492+00:00
-- elapsed: 132ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.stg_customers
-- query_id: not available
-- desc: get_relation > list_relations call
select
    table_catalog as database,
    table_name as name,
    table_schema as schema,
    'table' as type
from information_schema.tables
where table_schema ilike 'analytics'
and table_type = 'BASE TABLE'
union all
select
    table_catalog as database,
    table_name as name,
    table_schema as schema,
    case
    when view_definition ilike '%create materialized view%'
        then 'materialized_view'
    else 'view'
    end as type
from information_schema.views
where table_schema ilike 'analytics';
-- created_at: 2026-06-09T23:46:27.339153+00:00
-- finished_at: 2026-06-09T23:46:28.360732+00:00
-- elapsed: 1.0s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.stg_applications_dim
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.stg_applications_dim", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
create or replace view "dev"."analytics"."stg_applications_dim" as (
    with source as (
    select * from "dev"."public"."dim_applications"
),

renamed as (
    select
        customer_id,
        contract_type,
        credit_amount,
        annuity_amount,
        goods_price,
        ext_source_1,
        ext_source_2,
        ext_source_3,
        ext_source_mean
    from source
)

select * from renamed
  ) ;
-- created_at: 2026-06-09T23:46:27.687300+00:00
-- finished_at: 2026-06-09T23:46:28.647364+00:00
-- elapsed: 960ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.stg_customers
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.stg_customers", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
create or replace view "dev"."analytics"."stg_customers" as (
    with source as (
    select * from "dev"."public"."dim_customers"
),

renamed as (
    select
        customer_id,
        age_years,
        income_total,
        income_type,
        education_type,
        family_status,
        family_members,
        employment_years,
        region_rating
    from source
)

select * from renamed
  ) ;
-- created_at: 2026-06-09T23:46:28.002894+00:00
-- finished_at: 2026-06-09T23:46:29.218373+00:00
-- elapsed: 1.2s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_loan_performance
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_loan_performance", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
create  table
    "dev"."analytics"."mart_loan_performance__dbt_tmp"
    
    
    
  as (
    with base as (
    select * from "dev"."analytics"."stg_applications"
),

final as (
    select
        contract_type,
        income_type,
        education_type,
        region_rating,
        count(*)                                    as total_applications,
        sum(target)                                 as total_defaults,
        round(avg(target) * 100, 2)                 as default_rate_pct,
        round(avg(credit_amount), 2)                as avg_credit_amount,
        round(avg(annuity_amount), 2)               as avg_annuity_amount,
        round(avg(income_total), 2)                 as avg_income,
        round(avg(debt_to_income_ratio), 4)         as avg_debt_to_income,
        round(avg(ext_source_mean), 4)              as avg_ext_source_score
    from base
    group by 1, 2, 3, 4
)

select * from final
  );
-- created_at: 2026-06-09T23:46:27.700880+00:00
-- finished_at: 2026-06-09T23:46:29.554262+00:00
-- elapsed: 1.9s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_application_funnel
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_application_funnel", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
create  table
    "dev"."analytics"."mart_application_funnel__dbt_tmp"
    
    
    
  as (
    with base as (
    select * from "dev"."analytics"."stg_applications"
),

funnel as (
    select
        contract_type,
        income_type,
        region_rating,
        count(*)                                    as total_applications,
        sum(case when target = 0 then 1 else 0 end) as approved_no_default,
        sum(target)                                 as defaults,
        round(avg(target) * 100, 2)                 as default_rate_pct,
        round(avg(credit_amount), 2)                as avg_loan_amount,
        round(avg(income_total), 2)                 as avg_income,
        round(min(credit_amount), 2)                as min_loan_amount,
        round(max(credit_amount), 2)                as max_loan_amount,
        round(avg(debt_to_income_ratio), 4)         as avg_dti
    from base
    group by 1, 2, 3
)

select * from funnel
  );
-- created_at: 2026-06-09T23:46:28.369721+00:00
-- finished_at: 2026-06-09T23:46:29.919632+00:00
-- elapsed: 1.5s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_customer_risk
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_customer_risk", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
create  table
    "dev"."analytics"."mart_customer_risk__dbt_tmp"
    
    
    
  as (
    with base as (
    select * from "dev"."analytics"."stg_applications"
),

risk_scored as (
    select
        customer_id,
        age_years,
        income_total,
        income_type,
        education_type,
        credit_amount,
        annuity_amount,
        debt_to_income_ratio,
        ext_source_mean,
        target,
        case
            when ext_source_mean >= 0.6 then 'Low Risk'
            when ext_source_mean >= 0.4 then 'Medium Risk'
            else 'High Risk'
        end as risk_tier,
        case
            when income_total < 90000  then 'Low Income'
            when income_total < 180000 then 'Mid Income'
            else 'High Income'
        end as income_band,
        case
            when debt_to_income_ratio < 0.2  then 'Low DTI'
            when debt_to_income_ratio < 0.4  then 'Medium DTI'
            else 'High DTI'
        end as dti_band
    from base
),

final as (
    select
        risk_tier,
        income_band,
        dti_band,
        income_type,
        education_type,
        count(*)                            as total_customers,
        sum(target)                         as total_defaults,
        round(avg(target) * 100, 2)         as default_rate_pct,
        round(avg(income_total), 2)         as avg_income,
        round(avg(credit_amount), 2)        as avg_credit_amount,
        round(avg(ext_source_mean), 4)      as avg_ext_score
    from risk_scored
    group by 1, 2, 3, 4, 5
)

select * from final
  );
-- created_at: 2026-06-09T23:46:29.220565+00:00
-- finished_at: 2026-06-09T23:46:30.271010+00:00
-- elapsed: 1.1s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_loan_performance
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_loan_performance", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
alter table "dev"."analytics"."mart_loan_performance" rename to "mart_loan_performance__dbt_backup";
-- created_at: 2026-06-09T23:46:29.555311+00:00
-- finished_at: 2026-06-09T23:46:30.683005+00:00
-- elapsed: 1.1s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_application_funnel
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_application_funnel", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
alter table "dev"."analytics"."mart_application_funnel__dbt_tmp" rename to "mart_application_funnel";
-- created_at: 2026-06-09T23:46:29.921661+00:00
-- finished_at: 2026-06-09T23:46:31.081849+00:00
-- elapsed: 1.2s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_customer_risk
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_customer_risk", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
alter table "dev"."analytics"."mart_customer_risk" rename to "mart_customer_risk__dbt_backup";
-- created_at: 2026-06-09T23:46:30.272413+00:00
-- finished_at: 2026-06-09T23:46:31.308085+00:00
-- elapsed: 1.0s
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_loan_performance
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_loan_performance", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
alter table "dev"."analytics"."mart_loan_performance__dbt_tmp" rename to "mart_loan_performance";
-- created_at: 2026-06-09T23:46:30.688237+00:00
-- finished_at: 2026-06-09T23:46:31.522134+00:00
-- elapsed: 833ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_application_funnel
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_application_funnel", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
drop table if exists "dev"."analytics"."mart_application_funnel__dbt_backup" cascade;
-- created_at: 2026-06-09T23:46:31.537661+00:00
-- finished_at: 2026-06-09T23:46:31.728928+00:00
-- elapsed: 191ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_application_funnel_contract_type.aab36b4691
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_application_funnel_contract_type.aab36b4691", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select contract_type
from "dev"."analytics"."mart_application_funnel"
where contract_type is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:31.537548+00:00
-- finished_at: 2026-06-09T23:46:31.728924+00:00
-- elapsed: 191ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_application_funnel_total_applications.5992e63800
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_application_funnel_total_applications.5992e63800", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_applications
from "dev"."analytics"."mart_application_funnel"
where total_applications is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:31.084014+00:00
-- finished_at: 2026-06-09T23:46:31.962460+00:00
-- elapsed: 878ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_customer_risk
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_customer_risk", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
alter table "dev"."analytics"."mart_customer_risk__dbt_tmp" rename to "mart_customer_risk";
-- created_at: 2026-06-09T23:46:31.310316+00:00
-- finished_at: 2026-06-09T23:46:32.305107+00:00
-- elapsed: 994ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_loan_performance
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_loan_performance", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
drop table if exists "dev"."analytics"."mart_loan_performance__dbt_backup" cascade;
-- created_at: 2026-06-09T23:46:32.316096+00:00
-- finished_at: 2026-06-09T23:46:32.426977+00:00
-- elapsed: 110ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_loan_performance_total_applications.1fc0b0c0a3
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_loan_performance_total_applications.1fc0b0c0a3", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_applications
from "dev"."analytics"."mart_loan_performance"
where total_applications is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:32.316078+00:00
-- finished_at: 2026-06-09T23:46:32.546422+00:00
-- elapsed: 230ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_loan_performance_default_rate_pct.042d8f9afa
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_loan_performance_default_rate_pct.042d8f9afa", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select default_rate_pct
from "dev"."analytics"."mart_loan_performance"
where default_rate_pct is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:32.315880+00:00
-- finished_at: 2026-06-09T23:46:32.547391+00:00
-- elapsed: 231ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_loan_performance_contract_type.5e24c9f9ef
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_loan_performance_contract_type.5e24c9f9ef", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select contract_type
from "dev"."analytics"."mart_loan_performance"
where contract_type is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:31.966511+00:00
-- finished_at: 2026-06-09T23:46:32.908807+00:00
-- elapsed: 942ms
-- outcome: success
-- dialect: redshift
-- node_id: model.banking_analytics.mart_customer_risk
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "model.banking_analytics.mart_customer_risk", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
drop table if exists "dev"."analytics"."mart_customer_risk__dbt_backup" cascade;
-- created_at: 2026-06-09T23:46:32.921950+00:00
-- finished_at: 2026-06-09T23:46:33.023416+00:00
-- elapsed: 101ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_customer_risk_risk_tier.756e26daa2
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_customer_risk_risk_tier.756e26daa2", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select risk_tier
from "dev"."analytics"."mart_customer_risk"
where risk_tier is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:32.920479+00:00
-- finished_at: 2026-06-09T23:46:33.024984+00:00
-- elapsed: 104ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.not_null_mart_customer_risk_income_band.5f2e15adca
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.not_null_mart_customer_risk_income_band.5f2e15adca", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select income_band
from "dev"."analytics"."mart_customer_risk"
where income_band is null



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:32.926817+00:00
-- finished_at: 2026-06-09T23:46:33.042798+00:00
-- elapsed: 115ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.accepted_values_mart_customer_risk_income_band__Low_Income__Mid_Income__High_Income.adf14925b8
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.accepted_values_mart_customer_risk_income_band__Low_Income__Mid_Income__High_Income.adf14925b8", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

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



  
  
      
    ) dbt_internal_test;
-- created_at: 2026-06-09T23:46:32.921950+00:00
-- finished_at: 2026-06-09T23:46:33.115573+00:00
-- elapsed: 193ms
-- outcome: success
-- dialect: redshift
-- node_id: test.banking_analytics.accepted_values_mart_customer_risk_risk_tier__Low_Risk__Medium_Risk__High_Risk.887e673360
-- query_id: not available
-- desc: execute adapter call
/* {"app": "dbt", "dbt_version": "2.0.0", "node_id": "test.banking_analytics.accepted_values_mart_customer_risk_risk_tier__Low_Risk__Medium_Risk__High_Risk.887e673360", "profile_name": "jaffle_shop_1", "target_name": "dev"} */
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



  
  
      
    ) dbt_internal_test;
