-- Target label distribution and class imbalance
SELECT 
    COUNT(*) AS total_applications,
    SUM(fraud_bool) AS fraud_cases,
    COUNT(*) - SUM(fraud_bool) AS legitimate_cases,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct,
    ROUND((COUNT(*) - SUM(fraud_bool)) * 1.0 / NULLIF(SUM(fraud_bool), 0), 1) AS imbalance_ratio
FROM 'data/raw/Base.csv';

-- Application volume and fraud rate across months
SELECT 
    month,
    COUNT(*) AS total_applications,
    SUM(fraud_bool) AS fraud_count,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct
FROM 'data/raw/Base.csv'
GROUP BY month
ORDER BY month ASC;

-- BAF encodes missing values as -1 (or negative values for balance transfers)
SELECT 
    COUNT(*) AS total_records,
    COUNT(CASE WHEN prev_address_months_count = -1 THEN 1 END) AS missing_prev_address_count,
    ROUND(COUNT(CASE WHEN prev_address_months_count = -1 THEN 1 END) * 100.0 / COUNT(*), 2) AS missing_prev_address_pct,
    
    COUNT(CASE WHEN intended_balcon_amount < 0 THEN 1 END) AS missing_intended_balcon_count,
    ROUND(COUNT(CASE WHEN intended_balcon_amount < 0 THEN 1 END) * 100.0 / COUNT(*), 2) AS missing_intended_balcon_pct,
    
    COUNT(CASE WHEN bank_months_count = -1 THEN 1 END) AS missing_bank_months_count,
    ROUND(COUNT(CASE WHEN bank_months_count = -1 THEN 1 END) * 100.0 / COUNT(*), 2) AS missing_bank_months_pct,
    
    COUNT(CASE WHEN session_length_in_minutes < 0 THEN 1 END) AS missing_session_length_count,
    ROUND(COUNT(CASE WHEN session_length_in_minutes < 0 THEN 1 END) * 100.0 / COUNT(*), 2) AS missing_session_length_pct,

    COUNT(CASE WHEN device_distinct_emails_8w = -1 THEN 1 END) AS missing_device_emails_count,
    ROUND(COUNT(CASE WHEN device_distinct_emails_8w = -1 THEN 1 END) * 100.0 / COUNT(*), 2) AS missing_device_emails_pct
FROM 'data/raw/Base.csv';

-- Core numerical feature bounds
SELECT 
    'income' AS metric,
    MIN(income) AS min_val,
    ROUND(AVG(income), 3) AS mean_val,
    MAX(income) AS max_val
FROM 'data/raw/Base.csv'
UNION ALL
SELECT 
    'customer_age' AS metric,
    MIN(customer_age) AS min_val,
    ROUND(AVG(customer_age), 1) AS mean_val,
    MAX(customer_age) AS max_val
FROM 'data/raw/Base.csv'
UNION ALL
SELECT 
    'credit_risk_score' AS metric,
    MIN(credit_risk_score) AS min_val,
    ROUND(AVG(credit_risk_score), 1) AS mean_val,
    MAX(credit_risk_score) AS max_val
FROM 'data/raw/Base.csv'
UNION ALL
SELECT 
    'proposed_credit_limit' AS metric,
    MIN(proposed_credit_limit) AS min_val,
    ROUND(AVG(proposed_credit_limit), 1) AS mean_val,
    MAX(proposed_credit_limit) AS max_val
FROM 'data/raw/Base.csv';
