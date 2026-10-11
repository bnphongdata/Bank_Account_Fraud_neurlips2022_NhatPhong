from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import lightgbm as lgb
from sklearn.metrics import roc_curve, precision_recall_curve

from src.models.evaluate import evaluate_fraud_model, print_evaluation_summary
from src.visualization.visualize import apply_theme

MODELS_DIR = Path("models")
FIGURES_DIR = Path("reports/figures")


def prepare_datasets(data_path: str = "data/processed/clean_base.csv"):
    df = pd.read_csv(data_path)

    categorical_cols = [
        "payment_type",
        "employment_status",
        "housing_status",
        "source",
        "device_os",
        "age_group"
    ]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    drop_cols = ["fraud_bool", "month"]
    feature_cols = [c for c in df.columns if c not in drop_cols]

    # Out-Of-Time split theo month
    train_mask = df["month"] <= 5
    val_mask = df["month"] == 6
    test_mask = df["month"] == 7

    X_train, y_train = df.loc[train_mask, feature_cols], df.loc[train_mask, "fraud_bool"].values
    X_val, y_val = df.loc[val_mask, feature_cols], df.loc[val_mask, "fraud_bool"].values
    X_test, y_test = df.loc[test_mask, feature_cols], df.loc[test_mask, "fraud_bool"].values

    print(f"Train (thang 0-5) : {len(X_train):,} dong (Gian lan: {y_train.sum():,})")
    print(f"Val   (thang 6)   : {len(X_val):,} dong (Gian lan: {y_val.sum():,})")
    print(f"Test  (thang 7)   : {len(X_test):,} dong (Gian lan: {y_test.sum():,})")

    return X_train, y_train, X_val, y_val, X_test, y_test, feature_cols


def train_lightgbm_model(X_train, y_train, X_val, y_val):
    model = lgb.LGBMClassifier(
        objective="binary",
        boosting_type="gbdt",
        n_estimators=180,
        learning_rate=0.04,
        num_leaves=45,
        max_depth=7,
        min_child_samples=50,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=15,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )

    print("\nHuan luyen LightGBM...")
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="auc",
        callbacks=[
            lgb.early_stopping(stopping_rounds=25, first_metric_only=True, verbose=True),
            lgb.log_evaluation(period=40)
        ]
    )

    best_iter = model.best_iteration_ if model.best_iteration_ else model.n_estimators
    print(f"Vong lap tot nhat: {best_iter}")
    return model


def plot_feature_importance(model, feature_cols, top_n: int = 20):
    apply_theme()
    importance = model.feature_importances_
    feat_imp = pd.DataFrame({
        "feature": feature_cols,
        "importance": importance
    }).sort_values(by="importance", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    sns.barplot(data=feat_imp, x="importance", y="feature", hue="feature", palette="Blues_r", legend=False, ax=ax)
    ax.set_title(f"Top {top_n} dac trung quan trong (LightGBM)", pad=14)
    ax.set_xlabel("So lan phan nhanh (Split count)")
    ax.set_ylabel("Dac trung")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "lgbm_feature_importance.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Luu bieu do -> {out_path}")
    plt.close(fig)


def plot_curves(y_test, y_pred_prob):
    apply_theme()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
    ax1.plot(fpr, tpr, color="#2563EB", lw=2, label="LightGBM")
    ax1.plot([0, 1], [0, 1], color="#94A3B8", linestyle="--")
    ax1.axvline(0.05, color="#DC2626", linestyle=":", label="FPR = 5%")
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate (Recall)")
    ax1.set_title("ROC Curve")
    ax1.legend(loc="lower right")

    precision, recall, _ = precision_recall_curve(y_test, y_pred_prob)
    baseline_pr = y_test.sum() / len(y_test)
    ax2.plot(recall, precision, color="#16A34A", lw=2, label="LightGBM")
    ax2.axhline(baseline_pr, color="#94A3B8", linestyle="--", label=f"Baseline ({baseline_pr*100:.2f}%)")
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel("Recall")
    ax2.set_ylabel("Precision")
    ax2.set_title("Precision - Recall Curve")
    ax2.legend(loc="upper right")

    out_path = FIGURES_DIR / "model_evaluation_curves.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Luu bieu do -> {out_path}")
    plt.close(fig)


def run_training_pipeline():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    X_train, y_train, X_val, y_val, X_test, y_test, feature_cols = prepare_datasets()

    model = train_lightgbm_model(X_train, y_train, X_val, y_val)

    val_probs = model.predict_proba(X_val)[:, 1]
    test_probs = model.predict_proba(X_test)[:, 1]

    val_metrics = evaluate_fraud_model(y_val, val_probs, dataset_name="Val (thang 6)")
    test_metrics = evaluate_fraud_model(y_test, test_probs, dataset_name="Test OOT (thang 7)")

    print_evaluation_summary(val_metrics)
    print_evaluation_summary(test_metrics)

    model_path = MODELS_DIR / "lgbm_fraud_model.joblib"
    joblib.dump(model, model_path)
    print(f"Luu model -> {model_path}")

    metrics_path = MODELS_DIR / "evaluation_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({"validation": val_metrics, "test_oot": test_metrics}, f, indent=2, ensure_ascii=False)
    print(f"Luu metrics -> {metrics_path}")

    plot_feature_importance(model, feature_cols)
    plot_curves(y_test, test_probs)

    return model, test_metrics


if __name__ == "__main__":
    run_training_pipeline()
