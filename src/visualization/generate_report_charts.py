"""
Script: src.visualization.generate_report_charts
Mô tả: Tự động tải dữ liệu sạch và xuất toàn bộ hệ thống biểu đồ phân tích phục vụ báo cáo.
"""

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
    print("[*] Đang đọc dữ liệu sạch từ data/processed/clean_base.parquet...")
    df = pd.read_parquet("data/processed/clean_base.parquet")
    print(f"[✓] Đã nạp {len(df):,} dòng.")

    # 1. Xu hướng theo tháng
    print("[*] Đang vẽ biểu đồ xu hướng theo tháng...")
    plot_monthly_trend(df, filename="fraud_trend_by_month.png")

    # 2. Gian lận theo Device OS
    print("[*] Đang vẽ biểu đồ theo Hệ điều hành (device_os)...")
    plot_fraud_by_category(
        df,
        cat_col="device_os",
        title="Tỷ Lệ Gian Lận & Số Lượng Đơn Theo Hệ Điều Hành (Device OS)",
        filename="device_os_fraud_rate.png"
    )

    # 3. Gian lận theo Housing Status
    print("[*] Đang vẽ biểu đồ theo Tình trạng nhà ở (housing_status)...")
    plot_fraud_by_category(
        df,
        cat_col="housing_status",
        title="Tỷ Lệ Gian Lận Theo Tình Trạng Nhà Ở (Housing Status)",
        filename="housing_status_fraud_rate.png"
    )

    # 4. Gian lận theo Employment Status
    print("[*] Đang vẽ biểu đồ theo Tình trạng việc làm (employment_status)...")
    plot_fraud_by_category(
        df,
        cat_col="employment_status",
        title="Tỷ Lệ Gian Lận Theo Tình Trạng Việc Làm (Employment Status)",
        filename="employment_status_fraud_rate.png"
    )

    # 5. Gian lận theo Age Group
    print("[*] Đang vẽ biểu đồ theo Nhóm tuổi (age_group)...")
    plot_fraud_by_category(
        df,
        cat_col="age_group",
        title="Tỷ Lệ Gian Lận Theo Phân Nhóm Độ Tuổi (Age Group)",
        filename="age_group_fraud_rate.png"
    )

    # 6. Ma trận tương quan (Correlation Heatmap)
    print("[*] Đang vẽ Ma trận tương quan...")
    features_for_corr = [
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
    plot_correlation_heatmap(df, features_for_corr, filename="correlation_heatmap.png")

    # 7. So sánh hiệu quả các Fraud Rules (Heuristics)
    print("[*] Đang vẽ Biểu đồ đánh giá các Rule Heuristic...")
    apply_theme()
    rule_data = pd.DataFrame([
        {"Rule": "Tỷ lệ cơ sở (Baseline)", "Fraud_Rate": 1.103, "Volume": 1000000},
        {"Rule": "Rule 1: Windows + Housing BA + No Prev Addr", "Fraud_Rate": 7.286, "Volume": 43509},
        {"Rule": "Rule 2: Low Similarity + Free Email + Foreign", "Fraud_Rate": 3.686, "Volume": 4124},
        {"Rule": "Rule 3: No Prior Bank + No Valid Phone", "Fraud_Rate": 3.594, "Volume": 10574},
    ])
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#94A3B8", "#DC2626", "#F97316", "#EA580C"]
    bars = ax.barh(rule_data["Rule"], rule_data["Fraud_Rate"], color=colors, height=0.55)
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.2f}%", (w, bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0), textcoords="offset points", ha="left", va="center",
                    fontweight="bold", color="#1E293B")

    ax.axvline(1.103, color="#64748B", linestyle="--", linewidth=1.5, label="Baseline (1.10%)")
    ax.set_xlabel("Tỷ Lệ Gian Lận (%)")
    ax.set_title("Đánh Giá Tỷ Lệ Bắt Gian Lận Của Các Bộ Quy Tắc (Fraud Rules)", pad=15)
    ax.set_xlim(0, 9)
    ax.legend(loc="lower right")
    save_or_show(fig, "fraud_rules_comparison.png")

    print("[✓] Hoàn tất tạo toàn bộ biểu đồ!")

if __name__ == "__main__":
    generate_all_charts()
