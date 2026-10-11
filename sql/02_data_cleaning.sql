-- Tạo View sạch: chuyển đổi sentinel -1 thành cờ nhị phân và giá trị NULL, tính toán tỷ lệ rủi ro
CREATE OR REPLACE VIEW v_cleaned_baf AS
SELECT
    fraud_bool,
    month,
    
    income,
    credit_risk_score,
    proposed_credit_limit,
    ROUND(proposed_credit_limit / NULLIF(income * 10000, 0), 2) AS credit_to_income_ratio,

    customer_age,
    CASE 
        WHEN customer_age <= 25 THEN '18-25'
        WHEN customer_age <= 35 THEN '26-35'
        WHEN customer_age <= 50 THEN '36-50'
        WHEN customer_age <= 65 THEN '51-65'
        ELSE '65+'
    END AS age_group,

    -- Lịch sử cư trú và thời gian ở địa chỉ
    CASE WHEN prev_address_months_count = -1 THEN 0 ELSE 1 END AS has_prev_address_history,
    CASE WHEN prev_address_months_count = -1 THEN NULL ELSE prev_address_months_count END AS clean_prev_address_months,
    CASE WHEN current_address_months_count = -1 THEN NULL ELSE current_address_months_count END AS clean_current_address_months,

    -- Quan hệ ngân hàng trước đó và đăng ký chuyển số dư nợ
    CASE WHEN bank_months_count = -1 THEN 0 ELSE 1 END AS has_prior_bank_account,
    CASE WHEN bank_months_count = -1 THEN NULL ELSE bank_months_count END AS clean_bank_months,
    
    CASE WHEN intended_balcon_amount < 0 THEN 0 ELSE 1 END AS has_intended_balcon,
    CASE WHEN intended_balcon_amount < 0 THEN 0.0 ELSE intended_balcon_amount END AS clean_intended_balcon_amount,

    -- Xác thực thông tin liên lạc khách hàng
    name_email_similarity,
    email_is_free,
    phone_home_valid,
    phone_mobile_valid,
    (phone_home_valid = 0 AND phone_mobile_valid = 0) AS has_no_valid_phone,

    -- Tốc độ nộp đơn và đột biến ngắn hạn
    velocity_6h,
    velocity_24h,
    velocity_4w,
    ROUND(velocity_6h / NULLIF(velocity_24h, 0), 3) AS velocity_surge_ratio,

    -- Thuộc tính phiên truy cập và thiết bị
    CASE WHEN session_length_in_minutes < 0 THEN NULL ELSE session_length_in_minutes END AS clean_session_length,
    keep_alive_session,
    device_os,
    source,
    foreign_request,
    CASE WHEN device_distinct_emails_8w = -1 THEN 1 ELSE device_distinct_emails_8w END AS clean_device_distinct_emails_8w,
    device_fraud_count,

    payment_type,
    employment_status,
    housing_status,
    has_other_cards

FROM 'data/raw/Base.csv';

-- Kiểm tra đối soát nhanh số lượng bản ghi view vừa tạo
SELECT 
    COUNT(*) AS total_clean_rows,
    SUM(fraud_bool) AS total_fraud,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct,
    COUNT(clean_prev_address_months) AS non_null_prev_address,
    COUNT(clean_bank_months) AS non_null_bank_months
FROM v_cleaned_baf;
