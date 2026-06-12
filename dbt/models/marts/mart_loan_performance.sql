with base as (
    select * from {{ ref('stg_applications') }}
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
