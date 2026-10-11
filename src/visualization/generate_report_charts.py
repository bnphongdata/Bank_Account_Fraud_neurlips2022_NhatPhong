from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.visualization.visualize import (
    apply_theme,
    save_or_show,
    plot_fraud_by_category,
    plot_monthly_trend,
    plot_correlation_heatmap
)

def generate_all_charts():
    df = pd.read_parquet("data/processed/clean_base.parquet")

    # Time series
    plot_monthly_trend(df, filename="fraud_trend_by_month.png")

    # Categorical distributions vs fraud rate
    plot_fraud_by_category(
        df,
        cat_col="device_os",
        title="Fraud Rate and Application Volume by Device OS",
        filename="device_os_fraud_rate.png"
    )
    plot_fraud_by_category(
        df,
        cat_col="housing_status",
        title="Fraud Rate by Housing Status",
        filename="housing_status_fraud_rate.png"
    )
    plot_fraud_by_category(
        df,
        cat_col="employment_status",
        title="Fraud Rate by Employment Status",
        filename="employment_status_fraud_rate.png"
    )
    plot_fraud_by_category(
        df,
        cat_col="age_group",
        title="Fraud Rate by Age Group",
        filename="age_group_fraud_rate.png"
    )

    # Correlation matrix
    corr_features = [
        "fraud_bool",
        "income",
        "name_email_similarity",
        "customer_age",
        "credit_risk_score",
        "proposed_credit_limit",
        "velocity_6h",
        "velocity_24h",
        "has_prev_address",
        "has_prior_bank_account",
        "email_is_free"
    ]
    plot_correlation_heatmap(df, corr_features, filename="correlation_heatmap.png")

    # Heuristic rules evaluation chart
    apply_theme()
    rule_data = pd.DataFrame([
        {"Rule": "Baseline", "Fraud_Rate": 1.103, "Volume": 1000000},
        {"Rule": "Rule 1: Windows + Housing BA + No Prev Addr", "Fraud_Rate": 7.286, "Volume": 43509},
        {"Rule": "Rule 2: Low Similarity + Free Email + Foreign", "Fraud_Rate": 3.686, "Volume": 4124},
        {"Rule": "Rule 3: No Prior Bank + No Valid Phone", "Fraud_Rate": 3.594, "Volume": 10574},
    ])
    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = ["#94A3B8", "#DC2626", "#F97316", "#EA580C"]
    bars = ax.barh(rule_data["Rule"], rule_data["Fraud_Rate"], color=colors, height=0.5)
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.2f}%", (w, bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0), textcoords="offset points", ha="left", va="center",
                    fontweight="bold", color="#1E293B", fontsize=9.5)

    ax.axvline(1.103, color="#64748B", linestyle="--", linewidth=1.2, label="Baseline (1.10%)")
    ax.set_xlabel("Fraud Rate (%)")
    ax.set_title("Fraud Detection Precision Across Heuristic Rules", pad=14)
    ax.set_xlim(0, 9)
    ax.legend(loc="lower right")
    save_or_show(fig, "fraud_rules_comparison.png")

if __name__ == "__main__":
    generate_all_charts()
