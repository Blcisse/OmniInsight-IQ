from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any

import json
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

try:
    # Prefer local package import
    from src.ai.model_training.save_load_model import load_model
except Exception:  # pragma: no cover - fallback if package path differs
    from ..model_training.save_load_model import load_model  # type: ignore

from .forecast_trainer import prepare_forecast_data


def forecast_future(
    model: Pipeline,
    history: pd.DataFrame,
    date_col: str,
    horizon_days: int,
) -> List[Dict[str, float]]:
    """Generate future forecasts given a trained index-based model and history.

    history must include `date_col` and be sortable.
    Returns list of { date, prediction } for horizon.
    """
    if history.empty:
        return []
    df = history[[date_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    n = len(df)
    future_idx = pd.Series(range(n, n + horizon_days), name="t").to_frame()
    preds = model.predict(future_idx)

    last_date = df[date_col].iloc[-1].date()
    out: List[Dict[str, float]] = []
    for i, val in enumerate(preds):
        out.append({
            "date": (last_date + timedelta(days=i + 1)).isoformat(),
            "prediction": float(max(val, 0.0)),
        })
    return out


def run_forecast(
    model_name: str,
    timeframe: int,
    *,
    models_dir: str | Path = "models",
    history: Optional[pd.DataFrame] = None,
    date_col: str = "date",
    target_col: str = "target",
    exog_cols: Optional[List[str]] = None,
) -> List[Dict[str, float]]:
    """Load the latest saved model and produce a forecast for `timeframe` days.

    Expects `history` with at least `date_col` and, if the model uses exogenous
    features, matching `exog_cols` present. Returns a list of {date, prediction}.
    """
    if history is None or history.empty:
        raise ValueError("history DataFrame is required and cannot be empty")

    model = load_model(models_dir=models_dir, name=model_name)

    # Build the expected input design: time index t plus any exogenous columns
    X, _, hist = prepare_forecast_data(history, date_col=date_col, target_col=target_col, exog_cols=exog_cols)
    # Use only the date ordering from history for next horizon
    # We rely on the model being index-based; generate future indices
    n = len(X)
    future_idx = pd.Series(range(n, n + timeframe), name="t").to_frame()
    # Append exogenous placeholders if provided
    if exog_cols:
        for c in exog_cols:
            # If exogenous provided, repeat last known value as naive hold for horizon
            last_val = history[c].iloc[-1] if c in history.columns and not history.empty else 0
            future_idx[c] = last_val

    preds = model.predict(future_idx)

    last_date = pd.to_datetime(hist[date_col].iloc[-1]).date()
    out: List[Dict[str, float]] = []
    for i, val in enumerate(preds):
        out.append({
            "date": (last_date + timedelta(days=i + 1)).isoformat(),
            "prediction": float(max(val, 0.0)),
        })
    return out


def get_forecast_accuracy(
    model_name: str,
    *,
    models_dir: str | Path = "models",
    history: pd.DataFrame,
    date_col: str = "date",
    target_col: str = "target",
    exog_cols: Optional[List[str]] = None,
    holdout: int = 7,
) -> Dict[str, float]:
    """Compute simple accuracy metrics on the last `holdout` points.

    Uses the fitted model to predict the last `holdout` points and returns
    MAE, RMSE, and MAPE. Requires `history` with true `target_col` values.
    """
    if history is None or history.empty:
        raise ValueError("history DataFrame is required and cannot be empty")
    if holdout <= 0:
        raise ValueError("holdout must be positive")

    model = load_model(models_dir=models_dir, name=model_name)
    X, y, _ = prepare_forecast_data(history, date_col=date_col, target_col=target_col, exog_cols=exog_cols)
    if len(X) <= holdout:
        raise ValueError("history too short for requested holdout window")

    X_train, X_test = X.iloc[:-holdout], X.iloc[-holdout:]
    y_train, y_test = y.iloc[:-holdout], y.iloc[-holdout:]

    # Fit is idempotent if model already fitted; some pipelines may require refit
    try:
        model.fit(X_train, y_train)
    except Exception:
        pass

    preds = model.predict(X_test)
    y_true = y_test.to_numpy()
    y_pred = np.asarray(preds)

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    with np.errstate(divide="ignore", invalid="ignore"):
        mape_arr = np.abs((y_true - y_pred) / np.where(y_true == 0, np.nan, y_true)) * 100.0
        mape = float(np.nanmean(mape_arr))
    return {"mae": mae, "rmse": rmse, "mape": mape}


def export_forecast_results(
    forecast: List[Dict[str, Any]],
    path: str | Path,
    *,
    format: str = "csv",
) -> Path:
    """Export forecast list to CSV or JSON. Returns the written path."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if format.lower() == "json":
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(forecast, f, indent=2)
        return out_path
    # default CSV
    df = pd.DataFrame.from_records(forecast)
    df.to_csv(out_path, index=False)
    return out_path
