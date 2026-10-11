from pathlib import Path
import os
import pandas as pd
import duckdb
import pyarrow.csv as pv
import pyarrow as pa

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")


def get_available_datasets() -> list[str]:
    """Lấy danh sách các tệp CSV hiện có trong data/raw/."""
    if not RAW_DATA_DIR.exists():
        return []
    return [f.name for f in RAW_DATA_DIR.glob("*.csv")]


def load_raw_dataset(
    dataset_name: str = "Base.csv",
    use_arrow: bool = True,
    optimize_memory: bool = True,
    sample_rows: int | None = None
) -> pd.DataFrame:
    """Đọc dữ liệu thô từ data/raw/ bằng PyArrow và tự động tối ưu kiểu dữ liệu."""
    file_path = RAW_DATA_DIR / dataset_name
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    if use_arrow and sample_rows is None:
        table = pv.read_csv(str(file_path))
        df = table.to_pandas()
    else:
        df = pd.read_csv(file_path, nrows=sample_rows)

    if optimize_memory:
        df = downcast_dtypes(df)

    mem_mb = df.memory_usage().sum() / (1024 ** 2)
    print(f"Đã đọc {file_path.name}: {df.shape[0]:,} dòng x {df.shape[1]} cột ({mem_mb:.1f} MB)")
    return df


def downcast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Ép kiểu dữ liệu số và biến đổi các chuỗi ít giá trị sang category để giảm RAM."""
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
    """Thực thi câu truy vấn SQL trực tiếp qua DuckDB trên các tệp dữ liệu."""
    conn = duckdb.connect()
    return conn.execute(sql_query).df()


if __name__ == "__main__":
    print("Danh sách file thô:", get_available_datasets())
    sample_df = load_raw_dataset("Base.csv", sample_rows=1000)
    print(sample_df.head())
