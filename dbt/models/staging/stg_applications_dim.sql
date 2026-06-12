with source as (
    select * from {{ source('banking', 'dim_applications') }}
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
