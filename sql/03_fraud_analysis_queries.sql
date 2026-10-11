-- ==============================================================================
-- 03_FRAUD_ANALYSIS_QUERIES.SQL
-- Dự án: Bank Account Fraud Detection (NeurIPS 2022)
-- Mô tả: Các câu truy vấn phân tích chuyên sâu các mô hình gian lận (Fraud Patterns & Insights)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- INSIGHT 1: Phân tích tỷ lệ gian lận theo Hệ điều hành (Device OS) & Nguồn (Source)
-- ------------------------------------------------------------------------------
SELECT 
    device_os,
    source,
    COUNT(*) AS total_applications,
    SUM(fraud_bool) AS fraud_cases,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct,
    ROUND(SUM(fraud_bool) * 100.0 / SUM(SUM(fraud_bool)) OVER(), 2) AS pct_of_all_frauds
FROM 'data/raw/Base.csv'
GROUP BY device_os, source
ORDER BY fraud_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- INSIGHT 2: Ma trận rủi ro giữa Tình trạng nhà ở (Housing Status) & Việc làm
-- ------------------------------------------------------------------------------
SELECT 
    housing_status,
    employment_status,
    COUNT(*) AS total_applications,
    SUM(fraud_bool) AS fraud_count,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct
FROM 'data/raw/Base.csv'
GROUP BY housing_status, employment_status
HAVING COUNT(*) > 1000
ORDER BY fraud_rate_pct DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- INSIGHT 3: Tương quan giữa Độ tương đồng Tên - Email và Loại Email (Free vs Corporate)
-- Giả thuyết: Gian lận thường dùng email rác (similarity thấp) hoặc email miễn phí
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN name_email_similarity < 0.2 THEN '0.0 - 0.2 (Rất thấp)'
        WHEN name_email_similarity < 0.4 THEN '0.2 - 0.4 (Thấp)'
        WHEN name_email_similarity < 0.6 THEN '0.4 - 0.6 (Trung bình)'
        WHEN name_email_similarity < 0.8 THEN '0.6 - 0.8 (Khá)'
        ELSE '0.8 - 1.0 (Rất cao)'
    END AS similarity_tier,
    email_is_free,
    COUNT(*) AS total_apps,
    SUM(fraud_bool) AS fraud_cases,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct
FROM 'data/raw/Base.csv'
GROUP BY 1, 2
ORDER BY 1, 2;


-- ------------------------------------------------------------------------------
-- INSIGHT 4: Tốc độ đơn nộp (Velocity 6h vs Velocity 24h) & Dấu hiệu tấn công Bots/Syndicate
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN velocity_6h < 2000 THEN 'Low (<2k)'
        WHEN velocity_6h < 5000 THEN 'Medium (2k-5k)'
        WHEN velocity_6h < 8000 THEN 'High (5k-8k)'
        ELSE 'Extreme (>=8k)'
    END AS velocity_tier,
    COUNT(*) AS total_apps,
    SUM(fraud_bool) AS fraud_cases,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct
FROM 'data/raw/Base.csv'
GROUP BY 1
ORDER BY fraud_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- INSIGHT 5: Top Rule Heuristic phát hiện gian lận độ chính xác cao (High Precision Rules)
-- ------------------------------------------------------------------------------
WITH scored_applications AS (
    SELECT 
        fraud_bool,
        -- Rule 1: Thiết bị Windows + Housing 'BA' + Không có lịch sử địa chỉ cũ
        (device_os = 'windows' AND housing_status = 'BA' AND prev_address_months_count = -1) AS rule_suspect_device_residence,
        
        -- Rule 2: Tên email không khớp (<0.3) + Email miễn phí + Yêu cầu từ nước ngoài
        (name_email_similarity < 0.3 AND email_is_free = 1 AND foreign_request = 1) AS rule_disposable_identity,

        -- Rule 3: Không có tài khoản cũ + Không có số điện thoại hợp lệ
        (bank_months_count = -1 AND phone_home_valid = 0 AND phone_mobile_valid = 0) AS rule_ghost_applicant
    FROM 'data/raw/Base.csv'
)
SELECT 
    'Rule 1: Windows + Housing BA + No Prev Address' AS rule_name,
    COUNT(CASE WHEN rule_suspect_device_residence THEN 1 END) AS triggered_count,
    SUM(CASE WHEN rule_suspect_device_residence THEN fraud_bool ELSE 0 END) AS fraud_caught,
    ROUND(AVG(CASE WHEN rule_suspect_device_residence THEN fraud_bool ELSE NULL END) * 100, 3) AS hit_rate_pct
FROM scored_applications
UNION ALL
SELECT 
    'Rule 2: Low Similarity + Free Email + Foreign Request' AS rule_name,
    COUNT(CASE WHEN rule_disposable_identity THEN 1 END) AS triggered_count,
    SUM(CASE WHEN rule_disposable_identity THEN fraud_bool ELSE 0 END) AS fraud_caught,
    ROUND(AVG(CASE WHEN rule_disposable_identity THEN fraud_bool ELSE NULL END) * 100, 3) AS hit_rate_pct
FROM scored_applications
UNION ALL
SELECT 
    'Rule 3: No Prior Bank + No Valid Phones' AS rule_name,
    COUNT(CASE WHEN rule_ghost_applicant THEN 1 END) AS triggered_count,
    SUM(CASE WHEN rule_ghost_applicant THEN fraud_bool ELSE 0 END) AS fraud_caught,
    ROUND(AVG(CASE WHEN rule_ghost_applicant THEN fraud_bool ELSE NULL END) * 100, 3) AS hit_rate_pct
FROM scored_applications;
