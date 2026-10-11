# Bank Account Fraud Detection (NeurIPS 2022)

Dự án phân tích dữ liệu và xây dựng hệ thống phát hiện gian lận mở tài khoản ngân hàng dựa trên bộ dữ liệu chuẩn NeurIPS 2022 Bank Account Fraud (BAF). Quy mô tập dữ liệu gồm 1,000,000 hồ sơ đăng ký mở tài khoản trực tuyến với tỷ lệ gian lận cơ sở 1.103% (mất cân bằng nhãn ~1:90).

---

## Cấu trúc thư mục

```text
BAF/
│
├── data/
│   ├── raw/                  # Dữ liệu thô gốc (Base.csv, Variant I-V.csv)
│   ├── processed/            # Dữ liệu sạch xuất định dạng CSV (clean_base.csv)
│   └── external/             # Bảng tra cứu, từ điển dữ liệu
│
├── notebooks/                # Jupyter Notebooks phục vụ phân tích và thử nghiệm
│   ├── 01_eda_and_cleaning.ipynb
│   ├── 02_fraud_deep_dive.ipynb
│   └── 03_model_training_and_evaluation.ipynb
│
├── src/                      # Mã nguồn Python tái sử dụng
│   ├── data/
│   │   └── load_data.py      # Tiện ích đọc dữ liệu tối ưu qua PyArrow và DuckDB
│   ├── features/
│   │   └── clean_and_engineer.py # Xử lý giá trị sentinel -1 và tạo biến đặc trưng
│   ├── models/
│   │   ├── evaluate.py       # Hàm tính toán chỉ số Recall@FPR, PR-AUC, Confusion Matrix
│   │   └── train_model.py    # Pipeline huấn luyện mô hình LightGBM theo Out-Of-Time split
│   └── visualization/
│       ├── visualize.py      # Hàm định dạng theme và vẽ đồ thị chuẩn
│       └── generate_report_charts.py # Script xuất tự động toàn bộ biểu đồ báo cáo
│
├── models/                   # Lưu trữ trọng số mô hình và kết quả đánh giá
│   ├── lgbm_fraud_model.joblib
│   └── evaluation_metrics.json
│
├── reports/                  # Báo cáo chuyên sâu và hình ảnh xuất bản
│   ├── figures/              # Biểu đồ phân tích và đường cong ROC/PR
│   └── fraud_analysis_report.md  # Báo cáo phân tích dữ liệu & hành vi gian lận
│
├── sql/                      # Các truy vấn SQL phân tích nghiệp vụ
│   ├── 01_data_profiling.sql # Thống kê mất cân bằng nhãn và tỷ lệ dữ liệu thiếu
│   ├── 02_data_cleaning.sql  # View làm sạch và chuẩn hóa biến
│   └── 03_fraud_analysis_queries.sql # Phân tích hành vi và kiểm thử quy tắc Heuristic
│
├── config/                   # Cấu hình dự án
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Hiệu năng mô hình (Model Performance)

Mô hình LightGBM Classifier được huấn luyện và đánh giá theo cơ chế phân chia ngoài thời gian (Out-Of-Time Split) để phản ánh chính xác điều kiện vận hành thực tế:
- Tập Train (Tháng 0 - 5): 794,989 hồ sơ
- Tập Validation (Tháng 6): 108,168 hồ sơ (dùng để tìm điểm dừng sớm Early Stopping)
- Tập Test OOT (Tháng 7): 96,843 hồ sơ (kiểm thử độc lập)

### Kết quả trên tập Test OOT (Tháng 7)

| Chỉ số đánh giá | Kết quả | Ý nghĩa nghiệp vụ |
| :--- | :---: | :--- |
| ROC-AUC | 0.8933 | Khả năng phân loại và xếp hạng rủi ro tổng thể đạt mức cao |
| Recall @ FPR = 5% | 55.32% | Bắt được 790 / 1,428 vụ gian lận chỉ với 5% hồ sơ thẩm định tăng cường |
| Precision @ FPR = 5% | 14.22% | Tỷ lệ trúng tăng gần 10 lần so với tỷ lệ ngẫu nhiên (1.47%) |
| Recall @ FPR = 1% | 25.00% | Bắt được 1/4 tổng số vụ gian lận ở luồng kiểm soát rủi ro nghiêm ngặt |
| PR-AUC | 0.1965 | Vượt trội so với đường cơ sở ngẫu nhiên (0.0147) |

---

## Hướng dẫn chạy dự án

### 1. Kích hoạt môi trường và cài đặt thư viện
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Tiền xử lý dữ liệu và tạo đặc trưng
Lệnh đọc dữ liệu thô data/raw/Base.csv, xử lý giá trị sentinel -1, sinh các biến rủi ro dẫn xuất và lưu vào data/processed/clean_base.csv:
```powershell
python -m src.features.clean_and_engineer
```

### 3. Xuất toàn bộ biểu đồ phân tích
Tạo các biểu đồ phân tích xu hướng theo tháng, rủi ro theo thiết bị, nơi ở và xuất ra thư mục reports/figures/:
```powershell
python -m src.visualization.generate_report_charts
```

### 4. Huấn luyện mô hình Machine Learning
Huấn luyện mô hình LightGBM, đánh giá trên tập kiểm thử ngoài thời gian, lưu trọng số vào models/lgbm_fraud_model.joblib và xuất biểu đồ đánh giá:
```powershell
python -m src.models.train_model
```
