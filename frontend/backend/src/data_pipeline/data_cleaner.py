from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd


def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: trim strings, unify column names, drop full-NA rows."""
    out = df.copy()
    # standardize column names to snake_case
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    # trim whitespace in object cols
    obj_cols = [c for c in out.columns if pd.api.types.is_object_dtype(out[c])]
    for c in obj_cols:
        out[c] = out[c].astype(str).str.strip()
        out[c] = out[c].replace({"": pd.NA})
    # drop rows that are entirely NA
    out = out.dropna(how="all")
    return out


def normalize_values(df: pd.DataFrame, *, cols: Optional[Iterable[str]] = None, method: str = "zscore") -> pd.DataFrame:
    """Normalize numeric columns by z-score or min-max.

    Returns a new DataFrame with normalized values for selected columns.
    """
    out = df.copy()
    num_cols = list(cols) if cols is not None else [c for c in out.columns if pd.api.types.is_numeric_dtype(out[c])]
    if method == "minmax":
        for c in num_cols:
            col = pd.to_numeric(out[c], errors="coerce")
            min_v, max_v = col.min(), col.max()
            denom = (max_v - min_v) if pd.notna(max_v) and pd.notna(min_v) else np.nan
            if denom == 0 or pd.isna(denom):
                out[c] = 0.0
            else:
                out[c] = (col - min_v) / denom
        return out
    # default z-score
    for c in num_cols:
        col = pd.to_numeric(out[c], errors="coerce")
        std = col.std(ddof=1)
        mean = col.mean()
        if std == 0 or pd.isna(std):
            out[c] = 0.0
        else:
            out[c] = (col - mean) / std
    return out


def enrich_with_external_sources(
    df: pd.DataFrame,
    *,
    external_df: Optional[pd.DataFrame] = None,
    on: Optional[str] = None,
    how: str = "left",
) -> pd.DataFrame:
    """Enrich a DataFrame by joining with an external lookup.

    If `external_df` is None, returns the original DataFrame.
    """
    if external_df is None:
        return df.copy()
    if not on:
        raise ValueError("Parameter 'on' is required to merge external sources")
    return df.merge(external_df, on=on, how=how)

