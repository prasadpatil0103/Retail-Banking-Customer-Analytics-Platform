with source as (
    select * from {{ source('banking', 'fact_loans') }}
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
