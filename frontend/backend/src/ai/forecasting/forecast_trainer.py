from __future__ import annotations

from typing import Tuple, Optional, List, Dict, Any

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import TimeSeriesSplit
from sklearn import metrics
import numpy as np


def prepare_time_index(df: pd.DataFrame, date_col: str, target_col: str) -> Tuple[pd.Series, pd.Series]:
    """Prepare sequential index X and target y from a time series DataFrame.

    Assumes df[date_col] is sortable; returns X as incremental integers [[0],[1],...]
    and y as the corresponding target values ordered by date.
    """
    work = df[[date_col, target_col]].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work = work.sort_values(date_col)
    y = work[target_col].astype(float).reset_index(drop=True)
    X = pd.Series(range(len(y)))
    return X.to_frame(name="t"), y


def train_linear_forecaster(df: pd.DataFrame, date_col: str, target_col: str) -> Pipeline:
    """Train a simple linear forecaster (scaled index -> target)."""
    X, y = prepare_time_index(df, date_col, target_col)
    pipe = Pipeline(steps=[
        ("scale", StandardScaler(with_mean=False)),
        ("lr", LinearRegression()),
    ])
    pipe.fit(X, y)
    return pipe


def prepare_forecast_data(
    df: pd.DataFrame,
    date_col: str,
    target_col: str,
    *,
    exog_cols: Optional[List[str]] = None,
    freq: Optional[str] = None,
    agg: str = "sum",
    fill_method: str = "ffill",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Prepare time-ordered data for forecasting.

    - Parses and sorts by `date_col`
    - Optional resampling to a fixed frequency with aggregation (sum/mean)
    - Builds design matrix X with a time index 't' plus optional exogenous features
    Returns (X, y, history_df)
    """
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work = work.sort_values(date_col)

    if freq:
        if agg == "sum":
            work = work.set_index(date_col).resample(freq).sum(numeric_only=True).reset_index()
        else:
            work = work.set_index(date_col).resample(freq).mean(numeric_only=True).reset_index()
        # If target not present post-resample, raise
        if target_col not in work.columns:
            raise KeyError(f"Target '{target_col}' missing after resample")

    # Fill missing exogenous features
    exog_cols = exog_cols or []
    for c in exog_cols:
        if c in work.columns:
            work[c] = work[c].fillna(method=fill_method)

    y = work[target_col].astype(float).reset_index(drop=True)
    t = pd.Series(range(len(work)), name="t")
    X_parts = [t.to_frame()]
    for c in exog_cols:
        if c in work.columns:
            X_parts.append(work[[c]].reset_index(drop=True))
    X = pd.concat(X_parts, axis=1)
    return X, y, work[[date_col, target_col] + [c for c in exog_cols if c in work.columns]]


def train_forecast_model(
    df: pd.DataFrame,
    date_col: str,
    target_col: str,
    *,
    exog_cols: Optional[List[str]] = None,
    estimator: Optional[Any] = None,
    freq: Optional[str] = None,
    agg: str = "sum",
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Train a forecast model on time index and optional exogenous features.

    Returns (fitted_pipeline, meta) where meta includes feature_names and rows.
    """
    X, y, hist = prepare_forecast_data(
        df, date_col, target_col, exog_cols=exog_cols, freq=freq, agg=agg
    )
    features = list(X.columns)
    est = estimator or LinearRegression()
    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler(with_mean=False))]), features)
        ],
        remainder="drop",
    )
    pipe = Pipeline(steps=[("pre", pre), ("model", est)])
    pipe.fit(X, y)
    meta = {"feature_names": features, "n_rows": int(len(y))}
    return pipe, meta


def cross_validate_forecast(
    df: pd.DataFrame,
    date_col: str,
    target_col: str,
    *,
    exog_cols: Optional[List[str]] = None,
    estimator: Optional[Any] = None,
    freq: Optional[str] = None,
    agg: str = "sum",
    folds: int = 3,
) -> Dict[str, Any]:
    """Time series cross-validation for the forecast model.

    Uses expanding window TimeSeriesSplit. Returns average MAE/RMSE and per-fold scores.
    """
    X, y, _ = prepare_forecast_data(df, date_col, target_col, exog_cols=exog_cols, freq=freq, agg=agg)
    est = estimator or LinearRegression()
    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler(with_mean=False))]), list(X.columns))
        ],
        remainder="drop",
    )
    pipe = Pipeline(steps=[("pre", pre), ("model", est)])

    tscv = TimeSeriesSplit(n_splits=max(2, folds))
    maes: List[float] = []
    rmses: List[float] = []
    for train_idx, test_idx in tscv.split(X):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
        pipe.fit(X_tr, y_tr)
        preds = pipe.predict(X_te)
        mae = metrics.mean_absolute_error(y_te, preds)
        rmse = float(np.sqrt(metrics.mean_squared_error(y_te, preds)))
        maes.append(float(mae))
        rmses.append(rmse)

    return {
        "folds": folds,
        "mae_per_fold": maes,
        "rmse_per_fold": rmses,
        "mae": float(np.mean(maes)) if maes else None,
        "rmse": float(np.mean(rmses)) if rmses else None,
    }
