import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix
)


def calculate_recall_at_fpr(y_true: np.ndarray, y_prob: np.ndarray, target_fpr: float = 0.05) -> tuple[float, float]:
    """Tính Recall tại mức FPR cố định theo chuẩn benchmark BAF."""
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    idx = np.where(fpr <= target_fpr)[0]
    if len(idx) == 0:
        return 0.0, 1.0
    best_idx = idx[-1]
    return float(tpr[best_idx]), float(thresholds[best_idx])


def evaluate_fraud_model(y_true: np.ndarray, y_prob: np.ndarray, dataset_name: str = "Test Set") -> dict:
    roc_auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    recall_at_5pct, thresh_5pct = calculate_recall_at_fpr(y_true, y_prob, target_fpr=0.05)
    recall_at_1pct, thresh_1pct = calculate_recall_at_fpr(y_true, y_prob, target_fpr=0.01)

    y_pred_5pct = (y_prob >= thresh_5pct).astype(int)
    cm = confusion_matrix(y_true, y_pred_5pct)
    tn, fp, fn, tp = cm.ravel()

    return {
        "dataset": dataset_name,
        "total_records": int(len(y_true)),
        "total_frauds": int(y_true.sum()),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "recall_at_fpr_5pct": round(recall_at_5pct * 100, 2),
        "thresh_at_fpr_5pct": round(thresh_5pct, 4),
        "recall_at_fpr_1pct": round(recall_at_1pct * 100, 2),
        "thresh_at_fpr_1pct": round(thresh_1pct, 4),
        "true_positives_5pct": int(tp),
        "false_positives_5pct": int(fp),
        "false_negatives_5pct": int(fn),
        "true_negatives_5pct": int(tn),
        "precision_at_5pct": round(tp / (tp + fp) * 100, 2) if (tp + fp) > 0 else 0.0
    }


def print_evaluation_summary(metrics: dict):
    print(f"\n--- Ket qua danh gia: {metrics['dataset']} ---")
    print(f"Quy mo        : {metrics['total_records']:,} ho so (Gian lan: {metrics['total_frauds']:,})")
    print(f"ROC-AUC       : {metrics['roc_auc']:.4f}")
    print(f"PR-AUC        : {metrics['pr_auc']:.4f}")
    print(f"Recall@FPR=5% : {metrics['recall_at_fpr_5pct']:.2f}% (Bat duoc: {metrics['true_positives_5pct']:,} vu)")
    print(f"Precision@5%  : {metrics['precision_at_5pct']:.2f}%")
    print(f"Recall@FPR=1% : {metrics['recall_at_fpr_1pct']:.2f}%")
    print(f"Nguong cat @5%: {metrics['thresh_at_fpr_5pct']:.4f}")
