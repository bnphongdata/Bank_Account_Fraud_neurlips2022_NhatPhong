"""
Module: src.features.clean_and_engineer
Mô tả: Pipeline làm sạch dữ liệu, xử lý giá trị Sentinel (-1),
       tạo đặc trưng mới (Feature Engineering) và xuất dữ liệu chuẩn hóa sang Parquet.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from src.data.load_data import load_raw_dataset, downcast_dtypes

PROCESSED_DATA_DIR = Path("data/processed")


def handle_sentinel_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Xử lý các giá trị Sentinel (-1) trong tập BAF:
    - Tạo các cờ cắm (missing indicator flags):
        + missing_prev_address: Khách không có lịch sử địa chỉ cũ
        + missing_intended_balcon: Khách không chuyển số dư
        + missing_bank_months: Khách hàng mới, chưa có lịch sử ngân hàng
    - Chuyển giá trị -1 sang NaN hoặc 0 (tùy ngữ cảnh miền nghiệp vụ).
    """
    df = df.copy()

    # 1. Địa chỉ trước đây (prev_address_months_count = -1)
    df["has_prev_address"] = (df["prev_address_months_count"] != -1).astype("int8")
    df["clean_prev_address_months"] = df["prev_address_months_count"].replace(-1, np.nan)

    # 2. Địa chỉ hiện tại (current_address_months_count = -1)
    df["clean_current_address_months"] = df["current_address_months_count"].replace(-1, np.nan)

    # 3. Số dư chuyển khoản dự kiến (intended_balcon_amount < 0)
    df["has_intended_balcon"] = (df["intended_balcon_amount"] >= 0).astype("int8")
    df["clean_intended_balcon_amount"] = df["intended_balcon_amount"].apply(lambda x: max(0.0, x))

    # 4. Lịch sử quan hệ với ngân hàng (bank_months_count = -1)
    df["has_prior_bank_account"] = (df["bank_months_count"] != -1).astype("int8")
    df["clean_bank_months"] = df["bank_months_count"].replace(-1, np.nan)

    # 5. Thời gian phiên giao dịch (session_length_in_minutes < 0)
    df["clean_session_length"] = df["session_length_in_minutes"].replace(-1, np.nan)

    # 6. Số lượng email thiết bị trong 8 tuần (device_distinct_emails_8w = -1)
    df["clean_device_emails_8w"] = df["device_distinct_emails_8w"].replace(-1, 1)

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo các biến phân tích rủi ro mới:
    - credit_to_income_ratio: Hạn mức tín dụng / Thu nhập
    - velocity_surge_ratio: Tỷ lệ vận tốc 6h / 24h
    - age_group: Phân nhóm độ tuổi
    - no_valid_phone: Không có bất kỳ điện thoại hợp lệ nào
    - high_risk_profile_flag: Tổ hợp các đặc trưng rủi ro cao
    """
    df = df.copy()

    # 1. Tỷ lệ Hạn mức / Thu nhập
    # income là tỷ lệ chuẩn hóa [0.1, 0.9], tính ước lượng tỷ lệ đòn bẩy
    df["credit_to_income_ratio"] = (df["proposed_credit_limit"] / (df["income"] * 10000 + 1e-5)).round(2)

    # 2. Tốc độ đơn nộp (Surge Ratio)
    df["velocity_surge_ratio"] = (df["velocity_6h"] / (df["velocity_24h"] + 1e-5)).round(3)

    # 3. Phân nhóm độ tuổi khách hàng
    age_bins = [0, 25, 35, 50, 65, 120]
    age_labels = ["18-25", "26-35", "36-50", "51-65", "65+"]
    df["age_group"] = pd.cut(df["customer_age"], bins=age_bins, labels=age_labels, right=True)

    # 4. Kiểm tra tính xác thực số điện thoại
    df["no_valid_phone"] = ((df["phone_home_valid"] == 0) & (df["phone_mobile_valid"] == 0)).astype("int8")

    # 5. Rule flag rủi ro cao từ phân tích hành vi
    df["high_risk_profile"] = (
        (df["device_os"] == "windows") & 
        (df["housing_status"] == "BA") & 
        (df["has_prev_address"] == 0)
    ).astype("int8")

    return df


def clean_and_transform_pipeline(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Thực hiện toàn bộ pipeline từ xử lý sentinel đến kỹ thuật đặc trưng và tối ưu RAM.
    """
    print("[*] Bắt đầu xử lý giá trị Sentinel (-1)...")
    cleaned_df = handle_sentinel_values(raw_df)

    print("[*] Bắt đầu tạo các biến phân tích mới (Feature Engineering)...")
    featured_df = engineer_features(cleaned_df)

    print("[*] Tối ưu hóa kiểu dữ liệu bộ nhớ...")
    optimized_df = downcast_dtypes(featured_df)

    return optimized_df


def process_and_save(dataset_name: str = "Base.csv", output_format: str = "parquet") -> Path:
    """
    Đọc data thô, chạy pipeline làm sạch, và lưu vào data/processed/.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_df = load_raw_dataset(dataset_name)
    processed_df = clean_and_transform_pipeline(raw_df)

    stem = Path(dataset_name).stem.replace(" ", "_").lower()
    if output_format == "parquet":
        output_path = PROCESSED_DATA_DIR / f"clean_{stem}.parquet"
        processed_df.to_parquet(output_path, index=False, engine="pyarrow")
    else:
        output_path = PROCESSED_DATA_DIR / f"clean_{stem}.csv"
        processed_df.to_csv(output_path, index=False)

    print(f"[✓] Đã lưu dữ liệu làm sạch tại: {output_path}")
    print(f"[i] Kích thước file: {output_path.stat().st_size / (1024**2):.2f} MB")
    return output_path


if __name__ == "__main__":
    process_and_save("Base.csv", output_format="parquet")
