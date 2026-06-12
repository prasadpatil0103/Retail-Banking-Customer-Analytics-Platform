
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