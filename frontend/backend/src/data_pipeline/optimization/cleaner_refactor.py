from __future__ import annotations

from typing import Iterable, Optional, Tuple, List
import gzip
import io
import json
import pandas as pd
import numpy as np


def adaptive_data_cleaning(df: pd.DataFrame, *, strategy: str = "light") -> pd.DataFrame:
    """Adapt cleaning intensity based on strategy.

    - light: trim strings, drop duplicate rows
    - aggressive: light + drop columns with >95% NA and rows with >50% NA
    """
    out = df.copy()
    obj_cols = [c for c in out.columns if pd.api.types.is_object_dtype(out[c])]
    for c in obj_cols:
        out[c] = out[c].astype(str).str.strip()
        out[c] = out[c].replace({"": pd.NA})
    out = out.drop_duplicates()

    if strategy.lower() == "aggressive":
        col_na = out.isna().mean()
        drop_cols = col_na[col_na > 0.95].index.tolist()
        if drop_cols:
            out = out.drop(columns=drop_cols)
        row_na = out.isna().mean(axis=1)
        out = out.loc[row_na <= 0.5]
    return out


def remove_redundant_columns(
    df: pd.DataFrame,
    *,
    uniqueness_thresh: float = 1.0,
    missing_thresh: float = 0.95,
) -> Tuple[pd.DataFrame, List[str]]:
    """Drop columns with a single unique value or excessive missingness.

    Returns (clean_df, dropped_columns).
    """
    out = df.copy()
    dropped: List[str] = []
    for c in list(out.columns):
        if out[c].nunique(dropna=True) <= 1:
            dropped.append(c)
            continue
        miss = out[c].isna().mean()
        if miss >= missing_thresh:
            dropped.append(c)
    if dropped:
        out = out.drop(columns=dropped)
    return out, dropped


def compress_dataset(
    df: pd.DataFrame,
    *,
    method: str = "csv_gzip",
    orient: str = "records",
) -> bytes:
    """Return a compressed bytes representation of the dataset.

    - method: 'csv_gzip' or 'json_gzip'
    """
    if method == "json_gzip":
        payload = json.dumps(df.to_dict(orient=orient), separators=(",", ":")).encode("utf-8")
    else:
        # default CSV
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        payload = csv_buf.getvalue().encode("utf-8")
    return gzip.compress(payload)

