with base as (
    select * from {{ ref('stg_applications') }}
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
