-- Tỷ lệ gian lận theo Hệ điều hành thiết bị và Nguồn tiếp cận
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

-- Phân tích chéo giữa Tình trạng cư trú và Tình trạng việc làm
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

-- Phân khoảng độ tương đồng Tên - Email kết hợp với loại tên miền Email
SELECT 
    CASE 
        WHEN name_email_similarity < 0.2 THEN '< 0.2'
        WHEN name_email_similarity < 0.4 THEN '0.2 - 0.4'
        WHEN name_email_similarity < 0.6 THEN '0.4 - 0.6'
        WHEN name_email_similarity < 0.8 THEN '0.6 - 0.8'
        ELSE '>= 0.8'
    END AS similarity_tier,
    email_is_free,
    COUNT(*) AS total_apps,
    SUM(fraud_bool) AS fraud_cases,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct
FROM 'data/raw/Base.csv'
GROUP BY 1, 2
ORDER BY 1, 2;

-- Phân bố lưu lượng tốc độ nộp hồ sơ trong 6 giờ
SELECT 
    CASE 
        WHEN velocity_6h < 2000 THEN 'Thấp (<2k)'
        WHEN velocity_6h < 5000 THEN 'Trung bình (2k-5k)'
        WHEN velocity_6h < 8000 THEN 'Cao (5k-8k)'
        ELSE 'Rất cao (>=8k)'
    END AS velocity_tier,
    COUNT(*) AS total_apps,
    SUM(fraud_bool) AS fraud_cases,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct
FROM 'data/raw/Base.csv'
GROUP BY 1
ORDER BY fraud_rate_pct DESC;

-- Đánh giá độ chính xác và số lượng kích hoạt của các bộ quy tắc Heuristic
WITH scored_applications AS (
    SELECT 
        fraud_bool,
        (device_os = 'windows' AND housing_status = 'BA' AND prev_address_months_count = -1) AS rule_suspect_device_residence,
        (name_email_similarity < 0.3 AND email_is_free = 1 AND foreign_request = 1) AS rule_disposable_identity,
        (bank_months_count = -1 AND phone_home_valid = 0 AND phone_mobile_valid = 0) AS rule_ghost_applicant
    FROM 'data/raw/Base.csv'
)
SELECT 
    'Rule 1: Windows + Nhà ở BA + Chưa có địa chỉ cũ' AS rule_name,
    COUNT(CASE WHEN rule_suspect_device_residence THEN 1 END) AS triggered_count,
    SUM(CASE WHEN rule_suspect_device_residence THEN fraud_bool ELSE 0 END) AS fraud_caught,
    ROUND(AVG(CASE WHEN rule_suspect_device_residence THEN fraud_bool ELSE NULL END) * 100, 3) AS hit_rate_pct
FROM scored_applications
UNION ALL
SELECT 
    'Rule 2: Khác tên email + Email miễn phí + Yêu cầu từ nước ngoài' AS rule_name,
    COUNT(CASE WHEN rule_disposable_identity THEN 1 END) AS triggered_count,
    SUM(CASE WHEN rule_disposable_identity THEN fraud_bool ELSE 0 END) AS fraud_caught,
    ROUND(AVG(CASE WHEN rule_disposable_identity THEN fraud_bool ELSE NULL END) * 100, 3) AS hit_rate_pct
FROM scored_applications
UNION ALL
SELECT 
    'Rule 3: Chưa có tài khoản cũ + Không có SĐT hợp lệ' AS rule_name,
    COUNT(CASE WHEN rule_ghost_applicant THEN 1 END) AS triggered_count,
    SUM(CASE WHEN rule_ghost_applicant THEN fraud_bool ELSE 0 END) AS fraud_caught,
    ROUND(AVG(CASE WHEN rule_ghost_applicant THEN fraud_bool ELSE NULL END) * 100, 3) AS hit_rate_pct
FROM scored_applications;
