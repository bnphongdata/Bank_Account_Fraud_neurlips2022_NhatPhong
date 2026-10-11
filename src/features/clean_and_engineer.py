from pathlib import Path
import numpy as np
import pandas as pd
from src.data.load_data import load_raw_dataset, downcast_dtypes

PROCESSED_DATA_DIR = Path("data/processed")


def handle_sentinel_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle -1 sentinels from BAF raw data and derive explicit presence flags."""
    df = df.copy()

    # Address history: -1 means no prior address recorded
    df["has_prev_address"] = (df["prev_address_months_count"] != -1).astype("int8")
    df["clean_prev_address_months"] = df["prev_address_months_count"].replace(-1, np.nan)
    df["clean_current_address_months"] = df["current_address_months_count"].replace(-1, np.nan)

    # Intended transfer balance: negative values represent no balance transfer requested
    df["has_intended_balcon"] = (df["intended_balcon_amount"] >= 0).astype("int8")
    df["clean_intended_balcon_amount"] = df["intended_balcon_amount"].apply(lambda x: max(0.0, x))

    # Prior banking relationship: -1 means new customer with no prior account history
    df["has_prior_bank_account"] = (df["bank_months_count"] != -1).astype("int8")
    df["clean_bank_months"] = df["bank_months_count"].replace(-1, np.nan)

    # Session length & device email count
    df["clean_session_length"] = df["session_length_in_minutes"].replace(-1, np.nan)
    df["clean_device_emails_8w"] = df["device_distinct_emails_8w"].replace(-1, 1)

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive operational risk ratios and heuristic indicator flags."""
    df = df.copy()

    # Leverage proxy: proposed credit limit over scaled income
    df["credit_to_income_ratio"] = (df["proposed_credit_limit"] / (df["income"] * 10000 + 1e-5)).round(2)

    # Velocity spike between 6h and 24h windows
    df["velocity_surge_ratio"] = (df["velocity_6h"] / (df["velocity_24h"] + 1e-5)).round(3)

    # Cohort age grouping
    age_bins = [0, 25, 35, 50, 65, 120]
    age_labels = ["18-25", "26-35", "36-50", "51-65", "65+"]
    df["age_group"] = pd.cut(df["customer_age"], bins=age_bins, labels=age_labels, right=True)

    # Contactability check
    df["no_valid_phone"] = ((df["phone_home_valid"] == 0) & (df["phone_mobile_valid"] == 0)).astype("int8")

    # High-risk profile heuristic: Windows user + Housing BA + no prior address history
    df["high_risk_profile"] = (
        (df["device_os"] == "windows") & 
        (df["housing_status"] == "BA") & 
        (df["has_prev_address"] == 0)
    ).astype("int8")

    return df


def clean_and_transform_pipeline(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = handle_sentinel_values(raw_df)
    df = engineer_features(df)
    return downcast_dtypes(df)


def process_and_save(dataset_name: str = "Base.csv", output_format: str = "parquet") -> Path:
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

    size_mb = output_path.stat().st_size / (1024 ** 2)
    print(f"Saved processed output -> {output_path} ({size_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    process_and_save("Base.csv", output_format="parquet")
