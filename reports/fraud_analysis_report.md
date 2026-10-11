# 📑 BÁO CÁO PHÂN TÍCH DỮ LIỆU & PHÁT HIỆN GIAN LẬN MỞ TÀI KHOẢN NGÂN HÀNG
**Dự án:** Bank Account Fraud (NeurIPS 2022)  
**Tập dữ liệu:** `Base.csv` (1,000,000 hồ sơ mở tài khoản ngân hàng)  
**Ngày thực hiện:** Tháng 10/2026  

---

## 1. TỔNG QUAN DỮ LIỆU & VẤN ĐỀ NGHIỆP VỤ (EXECUTIVE SUMMARY)

- **Quy mô tập dữ liệu:** 1,000,000 hồ sơ đăng ký mở tài khoản ngân hàng trực tuyến.
- **Tỷ lệ gian lận cơ sở (Base Fraud Rate):** **1.103%** (11,029 hồ sơ gian lận / 988,971 hồ sơ hợp lệ).
- **Mức độ mất cân bằng nhãn (Imbalance Ratio):** Xấp xỉ **1:90** (cứ 90 đơn hợp lệ mới có 1 đơn gian lận). Đây là thách thức điển hình trong bài toán Fraud Analytics và Credit Risk.
- **Khoảng thời gian:** 8 tháng (Tháng 0 đến Tháng 7).

---

## 2. QUY TRÌNH LÀM SẠCH DỮ LIỆU (DATA CLEANING PIPELINE)

### 2.1 Phát hiện giá trị Sentinel (-1)
Tập dữ liệu NeurIPS BAF không dùng `NULL` chuẩn mà mã hóa dữ liệu thiếu thông qua giá trị `-1`:
1. `prev_address_months_count = -1` (**71.29%**): Khách hàng không có lịch sử địa chỉ cũ (chưa từng chuyển nhà hoặc thiếu thông tin khai báo).
2. `intended_balcon_amount < 0` (**74.25%**): Khách hàng không có nhu cầu chuyển số dư nợ từ ngân hàng khác sang.
3. `bank_months_count = -1` (**25.36%**): Khách hàng mới (New-to-Bank), chưa từng có tài khoản trước đây.
4. `session_length_in_minutes < 0` (**0.20%**): Lỗi theo dõi phiên truy cập.

### 2.2 Xử lý và Kỹ thuật Đặc trưng (Feature Engineering)
- Tạo cờ nhị phân (Binary Missing Flags): `has_prev_address`, `has_intended_balcon`, `has_prior_bank_account`.
- Chuyển đổi các trường sentinel sang `NaN` để tránh làm sai lệch mô hình thống kê / mô hình cây.
- Tạo các tỷ lệ rủi ro:
  - `credit_to_income_ratio`: Tỷ lệ hạn mức tín dụng đề xuất trên thu nhập ước tính.
  - `velocity_surge_ratio`: Tỷ lệ gia tăng tốc độ đơn (`velocity_6h` / `velocity_24h`).
  - `no_valid_phone`: Cờ cắm hồ sơ không có cả điện thoại bàn lẫn điện thoại di động hợp lệ.
  - `age_group`: Phân nhóm độ tuổi (`18-25`, `26-35`, `36-50`, `51-65`, `65+`).

### 2.3 Hiệu quả lưu trữ & Định dạng xuất bản
- Dữ liệu sạch sau khi qua pipeline xử lý sentinel và tạo biến đặc trưng được xuất ra file `data/processed/clean_base.csv` phục vụ phân tích.

---

## 3. CÁC PHÁT HIỆN CHUYÊN SÂU (KEY ANALYTICAL INSIGHTS)

### 3.1 Xu hướng gian lận theo thời gian (Monthly Trend)
- Tỷ lệ gian lận có xu hướng **tăng dần theo thời gian**:
  - Tháng 2: **0.875%** (Thấp nhất)
  - Tháng 6: **1.341%**
  - Tháng 7: **1.475%** (Tăng **68%** so với tháng 2).
- *Khuyến nghị:* Các băng nhóm gian lận có dấu hiệu thích nghi và khai thác các kẽ hở onboarding sau các đợt phát hành sản phẩm.

### 3.2 Dấu chân thiết bị (Device OS Risk)
- **Windows:** Tỷ lệ gian lận lên tới **2.469%** (cao gấp **4.8 lần** so với Linux: 0.515% và cao hơn nhiều so với Macintosh: 1.397%).
- Phần lớn các công cụ tự động hóa hoặc máy ảo gian lận được vận hành trên nền tảng Windows.

### 3.3 Tình trạng cư trú (Housing Status)
- Nhóm `housing_status = 'BA'` có tỷ lệ gian lận đột biến: **3.747%** (cao gấp hơn **3.4 lần** tỷ lệ cơ sở và cao gấp 10 lần so với nhóm `BE`: 0.344%).

### 3.4 Định danh Email & Tên khách hàng (Identity Consistency)
- Khách hàng có độ tương đồng tên và email thấp (`name_email_similarity < 0.2`) kết hợp sử dụng nhà cung cấp email miễn phí (`email_is_free = 1`) có tỷ lệ gian lận cao hơn rõ rệt so với nhóm dùng email tổ chức/doanh nghiệp.

---

## 4. BỘ QUY TẮC PHÁT HIỆN GIAN LẬN ĐỀ XUẤT (HEURISTIC FRAUD RULES)

| Quy tắc (Rule Heuristic) | Mô tả điều kiện | Số đơn kích hoạt | Gian lận bắt được | Tỷ lệ chính xác (Precision) | Lift (So với Baseline 1.10%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Rule 1: Suspect Device & Residence** | `device_os = 'windows'` VÀ `housing_status = 'BA'` VÀ `has_prev_address = 0` | 43,509 | 3,170 | **7.29%** | **6.6x** |
| **Rule 2: Disposable Foreign Identity** | `name_email_similarity < 0.3` VÀ `email_is_free = 1` VÀ `foreign_request = 1` | 4,124 | 152 | **3.69%** | **3.3x** |
| **Rule 3: Ghost Applicant** | `has_prior_bank_account = 0` VÀ `no_valid_phone = 1` | 10,574 | 380 | **3.59%** | **3.2x** |

---

## 5. HỆ THỐNG BIỂU ĐỒ TRỰC QUAN ĐÃ XUẤT BẢN

Các biểu đồ chất lượng cao đã được tự động lưu trong thư mục `reports/figures/`:
1. `fraud_trend_by_month.png`: Xu hướng tỷ lệ gian lận qua 8 tháng.
2. `device_os_fraud_rate.png`: So sánh tỷ lệ gian lận và khối lượng hồ sơ theo hệ điều hành.
3. `housing_status_fraud_rate.png`: Rủi ro theo tình trạng nhà ở.
4. `employment_status_fraud_rate.png`: Rủi ro theo nhóm việc làm.
5. `age_group_fraud_rate.png`: Phân tích rủi ro theo độ tuổi.
6. `correlation_heatmap.png`: Ma trận tương quan giữa các biến số chính.
7. `fraud_rules_comparison.png`: Đánh giá hiệu quả của các Rule Heuristic.

---

## 6. KHUYẾN NGHỊ VẬN HÀNH (OPERATIONAL RECOMMENDATIONS)

1. **Step-up Authentication / KYC tăng cường:**
   - Khi hồ sơ kích hoạt **Rule 1** (Thiết bị Windows + Nhà ở nhóm BA + Không có địa chỉ cũ), hệ thống không nên duyệt tự động mà cần chuyển sang luồng eKYC nâng cao (xác thực sinh trắc học khuôn mặt qua video hoặc yêu cầu nộp hóa đơn điện nước/chứng minh nơi ở).
2. **Kiểm tra OTP & Thiết bị:**
   - Chặn các đơn đăng ký có `foreign_request = 1` khi khai báo thông tin nội địa nếu không có giải trình cư trú hợp lệ.
3. **Mô hình hóa ML kết hợp:**
   - Sử dụng tập dữ liệu đã làm sạch `data/processed/clean_base.csv` để huấn luyện các thuật toán phân lớp gradient boosting (LightGBM / XGBoost / CatBoost) tối ưu hóa theo chỉ số **PR-AUC** hoặc **Recall tại ngưỡng FPR = 5%**.
