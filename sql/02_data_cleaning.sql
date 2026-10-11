-- ==============================================================================
-- 02_DATA_CLEANING.SQL
-- Dự án: Bank Account Fraud Detection (NeurIPS 2022)
-- Mô tả: Làm sạch dữ liệu, xử lý giá trị Sentinel (-1), chuẩn hóa định dạng và tạo cờ cắm (flags)
-- ==============================================================================

-- Tạo bảng hoặc View sạch (Clean View)
CREATE OR REPLACE VIEW v_cleaned_baf AS
SELECT
    fraud_bool,
    month,
    
    -- 1. Thu nhập và rủi ro tín dụng
    income,
    credit_risk_score,
    proposed_credit_limit,
    ROUND(proposed_credit_limit / NULLIF(income * 10000, 0), 2) AS credit_to_income_ratio,

    -- 2. Độ tuổi và phân nhóm khách hàng
    customer_age,
    CASE 
        WHEN customer_age <= 25 THEN '18-25'
        WHEN customer_age <= 35 THEN '26-35'
        WHEN customer_age <= 50 THEN '36-50'
        WHEN customer_age <= 65 THEN '51-65'
        ELSE '65+'
    END AS age_group,

    -- 3. Xử lý dữ liệu địa chỉ (Sentinel -1)
    CASE WHEN prev_address_months_count = -1 THEN 0 ELSE 1 END AS has_prev_address_history,
    CASE WHEN prev_address_months_count = -1 THEN NULL ELSE prev_address_months_count END AS clean_prev_address_months,
    CASE WHEN current_address_months_count = -1 THEN NULL ELSE current_address_months_count END AS clean_current_address_months,

    -- 4. Xử lý lịch sử tài khoản ngân hàng và chuyển khoản số dư (Sentinel < 0)
    CASE WHEN bank_months_count = -1 THEN 0 ELSE 1 END AS has_prior_bank_account,
    CASE WHEN bank_months_count = -1 THEN NULL ELSE bank_months_count END AS clean_bank_months,
    
    CASE WHEN intended_balcon_amount < 0 THEN 0 ELSE 1 END AS has_intended_balcon,
    CASE WHEN intended_balcon_amount < 0 THEN 0.0 ELSE intended_balcon_amount END AS clean_intended_balcon_amount,

    -- 5. Định danh & Độ tin cậy thông tin liên lạc
    name_email_similarity,
    email_is_free,
    phone_home_valid,
    phone_mobile_valid,
    (phone_home_valid = 0 AND phone_mobile_valid = 0) AS has_no_valid_phone,

    -- 6. Tốc độ đơn đăng ký (Velocity features)
    velocity_6h,
    velocity_24h,
    velocity_4w,
    ROUND(velocity_6h / NULLIF(velocity_24h, 0), 3) AS velocity_surge_ratio,

    -- 7. Phiên duyệt web và thiết bị (Device & Session)
    CASE WHEN session_length_in_minutes < 0 THEN NULL ELSE session_length_in_minutes END AS clean_session_length,
    keep_alive_session,
    device_os,
    source,
    foreign_request,
    CASE WHEN device_distinct_emails_8w = -1 THEN 1 ELSE device_distinct_emails_8w END AS clean_device_distinct_emails_8w,
    device_fraud_count,

    -- 8. Phân loại hình thức thanh toán & việc làm
    payment_type,
    employment_status,
    housing_status,
    has_other_cards

FROM 'data/raw/Base.csv';

-- Kiểm tra kiểm thử view vừa tạo
SELECT 
    COUNT(*) AS total_clean_rows,
    SUM(fraud_bool) AS total_fraud,
    ROUND(AVG(fraud_bool) * 100, 3) AS fraud_rate_pct,
    COUNT(clean_prev_address_months) AS non_null_prev_address,
    COUNT(clean_bank_months) AS non_null_bank_months
FROM v_cleaned_baf;
