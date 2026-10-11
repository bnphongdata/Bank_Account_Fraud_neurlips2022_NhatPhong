"""
Module: src.data.load_data
Mô tả: Tải và nạp dữ liệu Bank Account Fraud (NeurIPS 2022) với hiệu năng cao,
       tối ưu hóa bộ nhớ RAM và hỗ trợ đọc trực tiếp nhiều tập dữ liệu (Base & Variants).
"""

from pathlib import Path
import os
import pandas as pd
import duckdb
import pyarrow.csv as pv
import pyarrow as pa

# Thư mục gốc dữ liệu
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")


def get_available_datasets() -> list[str]:
    """Liệt kê danh sách các file dữ liệu có trong data/raw/."""
    if not RAW_DATA_DIR.exists():
        return []
    return [f.name for f in RAW_DATA_DIR.glob("*.csv")]


def load_raw_dataset(
    dataset_name: str = "Base.csv",
    use_arrow: bool = True,
    optimize_memory: bool = True,
    sample_rows: int | None = None
) -> pd.DataFrame:
    """
    Tải tập dữ liệu từ data/raw/ sử dụng PyArrow để đạt tốc độ cao nhất (1M dòng < 2 giây).
    
    Args:
        dataset_name: Tên file (ví dụ: 'Base.csv', 'Variant I.csv')
        use_arrow: Sử dụng pyarrow engine thay vì pandas thuần
        optimize_memory: Tối ưu kiểu dữ liệu số nguyên và số thực để tiết kiệm RAM
        sample_rows: Số dòng nạp thử nghiệm (None nếu nạp toàn bộ)
    
    Returns:
        pd.DataFrame chứa dữ liệu
    """
    file_path = RAW_DATA_DIR / dataset_name
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    print(f"[*] Đang tải dữ liệu từ {file_path}...")

    if use_arrow and sample_rows is None:
        table = pv.read_csv(str(file_path))
        df = table.to_pandas()
    else:
        df = pd.read_csv(file_path, nrows=sample_rows)

    if optimize_memory:
        df = downcast_dtypes(df)

    print(f"[✓] Đã tải thành công: {df.shape[0]:,} dòng | {df.shape[1]} cột")
    print(f"[i] Dung lượng RAM: {df.memory_usage().sum() / (1024**2):.2f} MB")
    return df


def downcast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Giảm kích thước bộ nhớ bằng cách downcast các kiểu dữ liệu int64 sang int32/int16, float64 sang float32.
    """
    for col in df.columns:
        col_type = df[col].dtype
        if col_type == "int64":
            c_min = df[col].min()
            c_max = df[col].max()
            if c_min >= -128 and c_max <= 127:
                df[col] = df[col].astype("int8")
            elif c_min >= -32768 and c_max <= 32767:
                df[col] = df[col].astype("int16")
            elif c_min >= -2147483648 and c_max <= 2147483647:
                df[col] = df[col].astype("int32")
        elif col_type == "float64":
            df[col] = df[col].astype("float32")
        elif col_type == "object" and df[col].nunique() < 50:
            df[col] = df[col].astype("category")

    return df


def query_duckdb(sql_query: str) -> pd.DataFrame:
    """
    Thực thi truy vấn SQL trực tiếp qua DuckDB trên các file CSV hoặc view.
    """
    conn = duckdb.connect()
    return conn.execute(sql_query).df()


if __name__ == "__main__":
    print("Các tập dữ liệu sẵn có:", get_available_datasets())
    sample_df = load_raw_dataset("Base.csv", sample_rows=1000)
    print(sample_df.head())
