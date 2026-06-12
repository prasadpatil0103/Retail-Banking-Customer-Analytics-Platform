-- Drop tables if they exist (clean slate)
DROP TABLE IF EXISTS fact_loans CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;
DROP TABLE IF EXISTS dim_applications CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- Dimension: Customers
CREATE TABLE dim_customers (
    customer_id      BIGINT PRIMARY KEY,
    age_years        INTEGER,
    income_total     DECIMAL(18,2),
    income_type      VARCHAR(50),
    education_type   VARCHAR(50),
    family_status    VARCHAR(50),
    family_members   DECIMAL(5,1),
    employment_years INTEGER,
    region_rating    INTEGER
);

-- Dimension: Applications
CREATE TABLE dim_applications (
    customer_id      BIGINT PRIMARY KEY,
    contract_type    VARCHAR(50),
    credit_amount    DECIMAL(18,2),
    annuity_amount   DECIMAL(18,2),
    goods_price      DECIMAL(18,2),
    ext_source_1     DECIMAL(10,6),
    ext_source_2     DECIMAL(10,6),
    ext_source_3     DECIMAL(10,6),
    ext_source_mean  DECIMAL(10,6)
);

-- Dimension: Date
CREATE TABLE dim_date (
    date_key     INTEGER PRIMARY KEY,
    full_date    DATE,
    year         INTEGER,
    quarter      INTEGER,
    month        INTEGER,
    month_name   VARCHAR(20),
    day          INTEGER,
    day_of_week  VARCHAR(20)
);

-- Fact: Loans
CREATE TABLE fact_loans (
    loan_id                 BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id             BIGINT REFERENCES dim_customers(customer_id),
    date_key                INTEGER REFERENCES dim_date(date_key),
    target                  INTEGER,
    credit_amount           DECIMAL(18,2),
    annuity_amount          DECIMAL(18,2),
    income_total            DECIMAL(18,2),
    goods_price             DECIMAL(18,2),
    debt_to_income_ratio    DECIMAL(10,4),
    credit_income_ratio     DECIMAL(10,4),
    ext_source_mean         DECIMAL(10,6),
    contract_type           VARCHAR(50),
    income_type             VARCHAR(50),
    education_type          VARCHAR(50),
    region_rating           INTEGER,
    age_years               INTEGER,
    employment_years        INTEGER,
    ingestion_timestamp     TIMESTAMP
);