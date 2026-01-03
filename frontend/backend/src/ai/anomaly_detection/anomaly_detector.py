from __future__ import annotations

from typing import Iterable, List, Tuple, Dict, Any, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def _build_feature_matrix(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    drop_na: bool = True,
) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    """Extract numeric feature matrix X from DataFrame.

    Returns (X, feature_names, clean_df). Drops rows with NA in features if drop_na.
    """
    cols = list(feature_cols)
    work = df[cols].copy()
    if drop_na:
        work = work.dropna(axis=0, how="any")
    X = work.to_numpy(dtype=float)
    return X, cols, work


def detect_isolation_forest(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    *,
    contamination: float = 0.05,
    random_state: int = 42,
) -> Tuple[Pipeline, List[int], List[float], Dict[str, Any]]:
    """Fit IsolationForest for outlier detection.

    Returns (pipeline, labels, scores, meta):
      - labels: 1 for inliers, -1 for outliers
      - scores: anomaly scores (higher is less anomalous per sklearn), use negative for ranking
      - meta: configuration and feature names
    """
    X, cols, _ = _build_feature_matrix(df, feature_cols)
    pipe = Pipeline(steps=[("scale", StandardScaler()), ("iforest", IsolationForest(contamination=contamination, random_state=random_state))])
    pipe.fit(X)
    labels = pipe.named_steps["iforest"].predict(X).tolist()
    scores = pipe.named_steps["iforest"].decision_function(X).tolist()
    meta = {"contamination": float(contamination), "features": cols}
    return pipe, labels, scores, meta


def detect_statistical_zscore(series: pd.Series, threshold: float = 3.0) -> pd.DataFrame:
    """Detect outliers using z-score threshold.

    Returns a DataFrame with columns: index, value, z_score, is_anomaly.
    """
    s = pd.to_numeric(series, errors="coerce")
    mean = s.mean()
    std = s.std(ddof=1)
    if std == 0 or np.isnan(std):
        z = pd.Series(np.zeros(len(s)), index=s.index)
    else:
        z = (s - mean) / std
    out = pd.DataFrame({"index": s.index, "value": s.values, "z_score": z.values})
    out["is_anomaly"] = out["z_score"].abs() > threshold
    return out


def detect_statistical_iqr(series: pd.Series, k: float = 1.5) -> pd.DataFrame:
    """Detect outliers using IQR rule (Tukey fences).

    Returns a DataFrame with columns: index, value, lower, upper, is_anomaly.
    """
    s = pd.to_numeric(series, errors="coerce")
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    out = pd.DataFrame({"index": s.index, "value": s.values})
    out["lower"] = float(lower)
    out["upper"] = float(upper)
    out["is_anomaly"] = (out["value"] < lower) | (out["value"] > upper)
    return out


def detect_time_series_anomalies(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    *,
    method: str = "zscore",
    threshold: float = 3.0,
    iqr_k: float = 1.5,
) -> pd.DataFrame:
    """Detect anomalies in a time series column via z-score or IQR.

    Returns a DataFrame with date, value, and method-specific fields; only rows marked as anomalies are included.
    """
    work = df[[date_col, value_col]].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work = work.sort_values(date_col)
    s = work[value_col]

    if method.lower() == "iqr":
        res = detect_statistical_iqr(s, k=iqr_k)
        anomalies = res[res["is_anomaly"]].copy()
        anomalies["date"] = work[date_col].values
        anomalies.rename(columns={"value": value_col}, inplace=True)
        return anomalies[["date", value_col, "lower", "upper"]]
    else:
        res = detect_statistical_zscore(s, threshold=threshold)
        anomalies = res[res["is_anomaly"]].copy()
        anomalies["date"] = work[date_col].values
        anomalies.rename(columns={"value": value_col}, inplace=True)
        return anomalies[["date", value_col, "z_score"]]


def calculate_anomaly_score(
    dataset: pd.Series | pd.DataFrame,
    *,
    method: str = "zscore",
) -> pd.Series:
    """Compute a per-row anomaly score.

    - For Series: absolute z-score.
    - For DataFrame: compute absolute z-score per numeric column and take the
      row-wise maximum (most anomalous dimension). Non-numeric columns are ignored.
    Returns a pandas Series aligned to the input index named 'score'.
    """
    if isinstance(dataset, pd.Series):
        s = pd.to_numeric(dataset, errors="coerce")
        mean = s.mean()
        std = s.std(ddof=1)
        if std == 0 or np.isnan(std):
            score = pd.Series(np.zeros(len(s)), index=s.index, name="score")
        else:
            score = ((s - mean) / std).abs().rename("score")
        return score

    # DataFrame path
    df = dataset.copy()
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])] 
    if not num_cols:
        return pd.Series(np.zeros(len(df)), index=df.index, name="score")

    z_abs_frames: list[pd.Series] = []
    for c in num_cols:
        col = pd.to_numeric(df[c], errors="coerce")
        std = col.std(ddof=1)
        if std == 0 or np.isnan(std):
            z_abs = pd.Series(np.zeros(len(col)), index=col.index)
        else:
            z_abs = ((col - col.mean()) / std).abs()
        z_abs_frames.append(z_abs)

    z_abs_df = pd.concat(z_abs_frames, axis=1)
    z_abs_df.columns = num_cols
    score = z_abs_df.max(axis=1).rename("score")
    return score


def detect_anomalies(
    dataset: pd.Series | pd.DataFrame,
    threshold: float = 3.0,
    *,
    method: str = "zscore",
) -> pd.DataFrame:
    """Detect anomalies by thresholding the calculated anomaly score.

    Returns a DataFrame including the original data (when DataFrame input) or
    a single 'value' column (when Series input), plus 'score' and 'is_anomaly'.
    """
    score = calculate_anomaly_score(dataset, method=method)
    if isinstance(dataset, pd.Series):
        out = pd.DataFrame({"value": pd.to_numeric(dataset, errors="coerce"), "score": score})
        out["is_anomaly"] = out["score"] > threshold
        return out

    df = dataset.copy()
    df["score"] = score
    df["is_anomaly"] = df["score"] > threshold
    return df


def mark_outliers(
    dataset: pd.Series | pd.DataFrame,
    *,
    threshold: float = 3.0,
    method: str = "zscore",
    score_col: Optional[str] = None,
) -> pd.DataFrame:
    """Return a copy of the dataset with an 'is_outlier' flag.

    - If `score_col` is provided (and present in the DataFrame), uses it with
      the given threshold. Otherwise computes score via calculate_anomaly_score.
    - For Series input, returns a 2-column DataFrame with 'value' and 'is_outlier'.
    """
    if isinstance(dataset, pd.Series):
        s = pd.to_numeric(dataset, errors="coerce")
        score = calculate_anomaly_score(s, method=method)
        out = pd.DataFrame({"value": s, "is_outlier": score > threshold})
        return out

    df = dataset.copy()
    if score_col and score_col in df.columns:
        df["is_outlier"] = df[score_col] > threshold
        return df

    score = calculate_anomaly_score(df, method=method)
    df["is_outlier"] = score > threshold
    return df
