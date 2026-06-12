
-- ── KPI 1: Overall default rate ─────────────────────────────
SELECT
    COUNT(*)                            AS total_applications,
    SUM(target)                         AS total_defaults,
    ROUND(AVG(target) * 100, 2)         AS default_rate_pct,
    ROUND(AVG(credit_amount), 2)        AS avg_loan_amount,
    ROUND(AVG(income_total), 2)         AS avg_income,
    ROUND(AVG(annuity_amount), 2)       AS avg_annuity
FROM fact_loans;

-- ── KPI 2: Default rate by contract type ────────────────────
SELECT
    contract_type,
    COUNT(*)                            AS total_applications,
    SUM(target)                         AS total_defaults,
    ROUND(AVG(target) * 100, 2)         AS default_rate_pct,
    ROUND(AVG(credit_amount), 2)        AS avg_loan_amount
FROM fact_loans
GROUP BY contract_type
ORDER BY default_rate_pct DESC;

-- ── KPI 3: Default rate by income type ──────────────────────
SELECT
    income_type,
    COUNT(*)                            AS total_applications,
    ROUND(AVG(target) * 100, 2)         AS default_rate_pct,
    ROUND(AVG(income_total), 2)         AS avg_income,
    ROUND(AVG(credit_amount), 2)        AS avg_loan_amount
FROM fact_loans
GROUP BY income_type
ORDER BY default_rate_pct DESC;

-- ── KPI 4: Default rate by education type ───────────────────
SELECT
    education_type,
    COUNT(*)                            AS total_applications,
    ROUND(AVG(target) * 100, 2)         AS default_rate_pct,
    ROUND(AVG(income_total), 2)         AS avg_income
FROM fact_loans
GROUP BY education_type
ORDER BY default_rate_pct DESC;

-- ── KPI 5: Default rate by region rating ────────────────────
SELECT
    region_rating,
    COUNT(*)                            AS total_applications,
    ROUND(AVG(target) * 100, 2)         AS default_rate_pct,
    ROUND(AVG(credit_amount), 2)        AS avg_loan_amount
FROM fact_loans
GROUP BY region_rating
ORDER BY region_rating;

-- ── KPI 6: Risk tier summary ─────────────────────────────────
SELECT
    CASE
        WHEN ext_source_mean >= 0.6 THEN "Low Risk"
        WHEN ext_source_mean >= 0.4 THEN "Medium Risk"
        ELSE "High Risk"
    END AS risk_tier,
    COUNT(*)                            AS total_customers,
    ROUND(AVG(target) * 100, 2)         AS default_rate_pct,
    ROUND(AVG(credit_amount), 2)        AS avg_loan_amount,
    ROUND(AVG(income_total), 2)         AS avg_income
FROM fact_loans
GROUP BY 1
ORDER BY default_rate_pct;

-- ── KPI 7: Monthly default trend ────────────────────────────
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(f.loan_id)                    AS total_loans,
    ROUND(AVG(f.target) * 100, 2)       AS default_rate_pct,
    ROUND(AVG(f.credit_amount), 2)      AS avg_loan_amount
FROM fact_loans f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;
