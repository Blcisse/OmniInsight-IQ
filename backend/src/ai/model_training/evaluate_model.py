from __future__ import annotations

from typing import Dict, Optional, Any, List, Tuple

import numpy as np
from sklearn import metrics


def evaluate_regression(y_true, y_pred) -> Dict[str, float]:
    """Return common regression metrics: MAE, RMSE, R2."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mae = metrics.mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(metrics.mean_squared_error(y_true, y_pred)))
    r2 = metrics.r2_score(y_true, y_pred)
    return {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}


def evaluate_classification(y_true, y_pred, y_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
    """Return common classification metrics.

    Always includes accuracy; includes roc_auc when probabilities provided.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    acc = metrics.accuracy_score(y_true, y_pred)
    report = {"accuracy": float(acc)}
    if y_proba is not None:
        try:
            # Handle binary or multi-class ROC AUC with macro average
            if y_proba.ndim == 1 or y_proba.shape[1] == 1:
                auc = metrics.roc_auc_score(y_true, y_proba)
            else:
                auc = metrics.roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
            report["roc_auc"] = float(auc)
        except Exception:
            # Ignore if classes/probabilities are not suitable
            pass
    return report


def evaluate_model_metrics(
    y_true,
    y_pred,
    *,
    task: str = "classification",
    y_proba: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Unified evaluator returning key metrics per task.

    - task="classification": returns accuracy and macro-averaged F1 (plus ROC AUC if y_proba given)
    - task="regression": returns RMSE, MAE, and R2
    """
    if task == "regression":
        return evaluate_regression(y_true, y_pred)
    # default classification
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    acc = metrics.accuracy_score(y_true, y_pred)
    f1 = metrics.f1_score(y_true, y_pred, average="macro")
    out: Dict[str, float] = {"accuracy": float(acc), "f1": float(f1)}
    if y_proba is not None:
        try:
            if y_proba.ndim == 1 or y_proba.shape[1] == 1:
                auc = metrics.roc_auc_score(y_true, y_proba)
            else:
                auc = metrics.roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
            out["roc_auc"] = float(auc)
        except Exception:
            pass
    return out


def compare_models(
    metrics_by_name: Dict[str, Dict[str, float]],
    *,
    task: str = "classification",
    primary_metric: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare models based on a primary metric and return ranking + best.

    - For classification default metric is F1 (macro);
    - For regression default metric is RMSE (lower is better).
    Returns { "ranking": List[Tuple[name, score]], "best": name, "best_score": score }.
    """
    if primary_metric is None:
        primary_metric = "f1" if task == "classification" else "rmse"

    items: List[Tuple[str, float]] = []
    for name, m in metrics_by_name.items():
        if primary_metric not in m:
            continue
        items.append((name, float(m[primary_metric])))

    if not items:
        return {"ranking": [], "best": None, "best_score": None}

    # Sort: higher is better for all except rmse/mae
    if primary_metric.lower() in {"rmse", "mae", "mape"}:
        items.sort(key=lambda x: x[1])  # ascending
    else:
        items.sort(key=lambda x: x[1], reverse=True)  # descending

    best_name, best_score = items[0]
    return {"ranking": items, "best": best_name, "best_score": best_score}


def generate_report(
    metrics_by_name: Dict[str, Dict[str, float]],
    *,
    task: str = "classification",
    primary_metric: Optional[str] = None,
) -> str:
    """Generate a simple text report summarizing metrics and best model.

    Includes key metrics (accuracy/F1 for classification; RMSE/MAE/R2 for regression)
    and a ranking using the chosen primary metric.
    """
    comp = compare_models(metrics_by_name, task=task, primary_metric=primary_metric)
    lines: List[str] = []
    lines.append(f"Task: {task}")
    if comp["best"] is not None:
        lines.append(f"Best model: {comp['best']} (score={comp['best_score']:.4f})")
    lines.append("Metrics:")

    # Determine which fields to display prominently
    fields = ("accuracy", "f1") if task == "classification" else ("rmse", "mae", "r2")
    for name, m in metrics_by_name.items():
        vals = ", ".join(
            f"{k}={m[k]:.4f}" for k in fields if k in m
        )
        lines.append(f"- {name}: {vals}")

    # Ranking
    if comp["ranking"]:
        lines.append("Ranking:")
        rank_lines = [f"  {i+1}. {n} ({s:.4f})" for i, (n, s) in enumerate(comp["ranking"])]
        lines.extend(rank_lines)

    return "\n".join(lines)
