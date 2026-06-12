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