# Bank Account Fraud Analysis (NeurIPS 2022)

Dự án phân tích dữ liệu và phát hiện gian lận mở tài khoản ngân hàng dựa trên bộ dữ liệu NeurIPS 2022 (BAF).

---

## Cấu trúc thư mục

```text
BAF/
│
├── data/
│   ├── raw/                  # Dữ liệu thô gốc (Base.csv, Variant I-V.csv)
│   ├── processed/            # Dữ liệu sạch xuất định dạng CSV (clean_base.csv)
│   └── external/             # Bảng tra cứu phụ, từ điển dữ liệu
│
├── notebooks/                # Notebooks phân tích khám phá và chuyên sâu
│   ├── 01_eda_and_cleaning.ipynb
│   └── 02_fraud_deep_dive.ipynb
│
├── src/                      # Module Python dùng chung
│   ├── data/                 # Tiện ích đọc dữ liệu tối ưu qua PyArrow/DuckDB (load_data.py)
│   ├── features/             # Xử lý sentinel và tạo biến đặc trưng (clean_and_engineer.py)
│   └── visualization/        # Hàm vẽ biểu đồ và xuất báo cáo (visualize.py)
│
├── reports/                  # Báo cáo phân tích và hình ảnh xuất bản
│   ├── figures/              # Biểu đồ chất lượng cao xuất tự động
│   └── fraud_analysis_report.md
│
├── sql/                      # Truy vấn SQL độc lập (DuckDB / PostgreSQL)
│   ├── 01_data_profiling.sql
│   ├── 02_data_cleaning.sql
│   └── 03_fraud_analysis_queries.sql
│
├── config/                   # Cấu hình dự án
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Hướng dẫn chạy dự án

### 1. Kích hoạt môi trường và cài đặt thư viện
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Chạy pipeline làm sạch và tạo đặc trưng
```powershell
python -m src.features.clean_and_engineer
```

### 3. Xuất toàn bộ biểu đồ báo cáo
```powershell
python -m src.visualization.generate_report_charts
```
