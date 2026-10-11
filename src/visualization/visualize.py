from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

FIGURES_DIR = Path("reports/figures")


def apply_theme():
    """Thiết lập định dạng font, trục tọa độ và lưới hiển thị chuẩn cho đồ thị."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "medium",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 14,
        "figure.titleweight": "bold",
        "figure.dpi": 200,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
    })


def save_or_show(fig: plt.Figure, filename: str | None = None):
    """Lưu ảnh đồ thị ra thư mục reports/figures/ hoặc đóng figure."""
    if filename:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        out_path = FIGURES_DIR / filename
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        print(f"Đã lưu biểu đồ -> {out_path}")
    plt.close(fig)


def plot_fraud_by_category(
    df: pd.DataFrame,
    cat_col: str,
    title: str | None = None,
    filename: str | None = None,
    palette: str = "Blues_r"
):
    """Vẽ biểu đồ kết hợp số lượng đơn nộp và tỷ lệ gian lận theo từng nhóm danh mục."""
    apply_theme()
    stats = (
        df.groupby(cat_col, observed=True)
        .agg(
            total_apps=("fraud_bool", "count"),
            fraud_rate=("fraud_bool", lambda x: x.mean() * 100),
        )
        .reset_index()
        .sort_values(by="fraud_rate", ascending=False)
    )

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax2.grid(False)

    ax1.bar(
        stats[cat_col].astype(str),
        stats["total_apps"],
        color="#CBD5E1",
        alpha=0.6,
        width=0.45,
        label="Số lượng đơn"
    )

    ax2.plot(
        stats[cat_col].astype(str),
        stats["fraud_rate"],
        color="#E11D48",
        marker="o",
        linewidth=2,
        markersize=6,
        label="Tỷ lệ gian lận (%)"
    )

    for x, y in zip(stats[cat_col].astype(str), stats["fraud_rate"]):
        ax2.annotate(
            f"{y:.2f}%",
            (x, y),
            textcoords="offset points",
            xytext=(0, 7),
            ha="center",
            fontweight="bold",
            color="#BE123C",
            fontsize=9.5
        )

    ax1.set_ylabel("Tổng số hồ sơ", color="#475569")
    ax2.set_ylabel("Tỷ lệ gian lận (%)", color="#E11D48")
    ax1.set_xlabel(cat_col.replace("_", " ").title())
    ax1.set_title(title or f"Tỷ lệ gian lận theo {cat_col}", pad=14)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right")

    save_or_show(fig, filename)


def plot_monthly_trend(df: pd.DataFrame, filename: str = "fraud_trend_by_month.png"):
    """Vẽ xu hướng tỷ lệ gian lận và quy mô đơn nộp qua các tháng."""
    apply_theme()
    monthly = df.groupby("month").agg(
        total=("fraud_bool", "count"),
        fraud_rate=("fraud_bool", lambda x: x.mean() * 100)
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax2 = ax1.twinx()
    ax2.grid(False)

    ax1.bar(monthly["month"], monthly["total"], color="#94A3B8", alpha=0.4, width=0.4, label="Số lượng đơn")
    ax2.plot(monthly["month"], monthly["fraud_rate"], color="#DC2626", marker="s", linewidth=2.2, label="Tỷ lệ gian lận (%)")

    for x, y in zip(monthly["month"], monthly["fraud_rate"]):
        ax2.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0, 7), ha="center", fontweight="bold", color="#B91C1C", fontsize=9.5)

    ax1.set_title("Xu hướng gian lận theo tháng (Tháng 0 - 7)", pad=14)
    ax1.set_xlabel("Tháng")
    ax1.set_ylabel("Số lượng hồ sơ", color="#475569")
    ax2.set_ylabel("Tỷ lệ gian lận (%)", color="#DC2626")
    ax1.set_xticks(monthly["month"])

    save_or_show(fig, filename)


def plot_correlation_heatmap(df: pd.DataFrame, features: list[str], filename: str = "correlation_heatmap.png"):
    """Vẽ ma trận hệ số tương quan giữa các biến liên tục và nhãn gian lận."""
    apply_theme()
    corr = df[features].corr()

    fig, ax = plt.subplots(figsize=(9.5, 7.5))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        cmap="coolwarm",
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )
    ax.set_title("Ma trận tương quan giữa các đặc trưng", pad=14)
    save_or_show(fig, filename)
