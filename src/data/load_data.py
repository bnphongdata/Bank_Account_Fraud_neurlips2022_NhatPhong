from pathlib import Path
import os
import pandas as pd
import duckdb
import pyarrow.csv as pv
import pyarrow as pa

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")


def get_available_datasets() -> list[str]:
    if not RAW_DATA_DIR.exists():
        return []
    return [f.name for f in RAW_DATA_DIR.glob("*.csv")]


def load_raw_dataset(
    dataset_name: str = "Base.csv",
    use_arrow: bool = True,
    optimize_memory: bool = True,
    sample_rows: int | None = None
) -> pd.DataFrame:
    """Load BAF dataset from data/raw with optional pyarrow reader and dtype downcasting."""
    file_path = RAW_DATA_DIR / dataset_name
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if use_arrow and sample_rows is None:
        table = pv.read_csv(str(file_path))
        df = table.to_pandas()
    else:
        df = pd.read_csv(file_path, nrows=sample_rows)

    if optimize_memory:
        df = downcast_dtypes(df)

    mem_mb = df.memory_usage().sum() / (1024 ** 2)
    print(f"Loaded {file_path.name}: {df.shape[0]:,} rows x {df.shape[1]} cols ({mem_mb:.1f} MB)")
    return df


def downcast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast numeric types and convert low-cardinality strings to category to reduce RAM."""
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
    """Helper to run DuckDB SQL queries directly on CSV/Parquet."""
    conn = duckdb.connect()
    return conn.execute(sql_query).df()


if __name__ == "__main__":
    print("Available raw files:", get_available_datasets())
    sample_df = load_raw_dataset("Base.csv", sample_rows=1000)
    print(sample_df.head())
