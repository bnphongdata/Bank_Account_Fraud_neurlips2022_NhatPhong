# KẾ HOẠCH XÂY DỰNG MÔ HÌNH MACHINE LEARNING DỰ ĐOÁN GIAN LẬN (FRAUD DETECTION)
**Dự án:** Bank Account Fraud (NeurIPS 2022)  
**Dữ liệu đầu vào:** `data/processed/clean_base.csv` (1,000,000 bản ghi)  
**Tập kiểm thử trôi dạt (Stress Test):** `Variant I.csv` đến `Variant V.csv`  

---

## 1. MỤC TIÊU & ĐỊNH NGHĨA BÀI TOÁN (PROBLEM FORMULATION)

### 1.1 Bản chất bài toán
- **Dạng bài toán:** Phân loại nhị phân (Binary Classification) có giám sát.
- **Nhãn mục tiêu (`y`):** `fraud_bool` (0: Khách hàng hợp lệ, 1: Hồ sơ gian lận).
- **Thách thức cốt lõi:**
  - **Mất cân bằng dữ liệu cực đoan:** Tỷ lệ gian lận chỉ **1.103%** (~1:90).
  - **Dịch chuyển phân phối theo thời gian (Temporal Concept Drift):** Tỷ lệ gian lận tăng dần từ tháng 2 (0.88%) đến tháng 7 (1.48%).

### 1.2 Chỉ số đánh giá (Evaluation Metrics)

1. **Chỉ số kỹ thuật chính (Primary Metric - Chuẩn NeurIPS 2022):**
   - **Recall tại ngưỡng FPR = 5% (Recall@FPR=5%):** Trong điều kiện ngân hàng chỉ chấp nhận làm phiền tối đa 5% khách hàng tốt để xác minh thêm, mô hình bắt được bao nhiêu % tổng số vụ gian lận.
   - **PR-AUC (Precision-Recall AUC):** Đo lường sự cân bằng giữa tỷ lệ bắt trúng (Precision) và tỷ lệ bao phủ gian lận (Recall) trên toàn dải ngưỡng.
2. **Chỉ số kinh doanh (Business Impact Metric):**
   - **Tỷ lệ giảm thiểu thiệt hại (Fraud Loss Prevention Rate):** Tổng giá trị hạn mức tín dụng gian lận bị chặn lại.
   - **Tỷ lệ phê duyệt tự động (Straight-Through Processing - STP Rate):** Tỷ lệ hồ sơ tốt được duyệt ngay lập tức mà không cần thẩm định thủ công.

---

## 2. CHIẾN LƯỢC PHÂN CHIA DỮ LIỆU (OUT-OF-TIME SPLIT)

Dữ liệu được chia theo trục thời gian thực (`month`):

```text
clean_base.csv (1M rows)
  ├── Train Set (Months 0-4)      : ~675,000 dong (huan luyen trong so)
  ├── Validation Set (Months 5-6) : ~227,000 dong (chinh threshold & hyperparams)
  └── Test Set OOT (Month 7)      : ~97,000 dong (danh gia doc lap ngoai thoi gian)
```

---

## 3. LỘ TRÌNH TRIỂN KHAI THEO 5 GIAI ĐOẠN

### Giai đoạn 1: Chuẩn bị Dữ liệu & Pipeline Tiền Xử Lý
- Tách tập dữ liệu theo thời gian (Train: Month 0-4, Val: Month 5-6, Test: Month 7).
- Xử lý biến danh mục (Categorical) cho các cột `device_os`, `housing_status`, `employment_status`, `payment_type`.
- Loại bỏ các cột định danh hoặc cột leakage: `month`.

### Giai đoạn 2: Xây dựng Mô hình Cơ sở (Baseline) & So Sánh Thuật Toán
- **Baseline Model:** Logistic Regression (có phạt L2) & Decision Tree.
- **Champion Models:** LightGBM, XGBoost, CatBoost.
- **So sánh hiệu năng:** Lập bảng tổng hợp so sánh chỉ số `PR-AUC`, `ROC-AUC`, `Recall@FPR=5%` trên tập Validation.

### Giai đoạn 3: Xử lý Mất Cân Bằng Nhãn & Tối Ưu Siêu Tham Số
- Cấu hình trọng số phạt lớp thiểu số trong hàm mất mát (`scale_pos_weight`).
- Tinh chỉnh các tham số chính bằng Optuna: learning_rate, max_depth, num_leaves, subsample, colsample_bytree.

### Giai đoạn 4: Thiết Kế Động Cơ Ra Quyết Định (Decision Engine)
Phân luồng 3 tầng theo ngưỡng xác suất:

| Phân tầng rủi ro | Dải xác suất dự báo (P) | Hành động của hệ thống | Trải nghiệm khách hàng |
| :--- | :---: | :--- | :--- |
| **Luồng Xanh (Low Risk)** | P < 0.15 | **Phê duyệt tự động (Auto-Approve)** | Mở tài khoản ngay lập tức (STP) |
| **Luồng Vàng (Medium Risk)** | 0.15 <= P < 0.65 | **Xác minh tăng cường (Step-up KYC)** | Yêu cầu Video Call / quét chip CCCD |
| **Luồng Đỏ (High Risk)** | P >= 0.65 | **Từ chối tự động (Auto-Decline)** | Chặn đơn đăng ký, cảnh báo danh sách đen |

### Giai đoạn 5: Giải Thích Mô Hình (SHAP Explainability) & Stress Testing
- SHAP Analysis: Trích xuất top đặc trưng quyết định và tạo Adverse Action Notice giải trình lý do từ chối.
- Stress Testing trên `Variant I - V` để kiểm tra độ trôi dạt (Concept Drift).

---

## 4. CẤU TRÚC CODE DỰ ÁN

```text
BAF/
│
├── src/
│   ├── models/                   # Module huấn luyện và đánh giá mô hình
│   │   ├── __init__.py
│   │   ├── train_model.py        # Pipeline huấn luyện LightGBM / XGBoost
│   │   └── evaluate.py           # Tính toán chỉ số Recall@FPR, PR-AUC
│
├── notebooks/
│   ├── 01_eda_and_cleaning.ipynb
│   ├── 02_fraud_deep_dive.ipynb
│   └── 03_model_training_and_evaluation.ipynb
│
├── models/                       # Lưu trữ trọng số mô hình đã train (.joblib, .json)
│   ├── lgbm_fraud_model.joblib
│   └── evaluation_metrics.json
│
└── reports/
    ├── ml_modeling_plan.md
    └── fraud_analysis_report.md
```
