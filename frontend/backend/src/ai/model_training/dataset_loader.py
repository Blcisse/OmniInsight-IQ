from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Any, Dict

import pandas as pd
from sklearn.model_selection import train_test_split


def load_dataset(path: str | Path, **read_kwargs) -> pd.DataFrame:
    """Load a dataset into a pandas DataFrame.

    Supports CSV, JSON, Parquet, and Excel based on file extension.
    Additional keyword arguments are forwarded to the corresponding pandas reader.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found: {p}")

    ext = p.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(p, **read_kwargs)
    if ext in {".json"}:
        return pd.read_json(p, **read_kwargs)
    if ext in {".parquet"}:
        return pd.read_parquet(p, **read_kwargs)
    if ext in {".xls", ".xlsx"}:
        return pd.read_excel(p, **read_kwargs)

    raise ValueError(f"Unsupported dataset extension: {ext}")


def train_test_split_df(
    df: pd.DataFrame,
    target: str,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split a DataFrame into train/test sets.

    If `stratify=True`, uses the target column for stratification (useful for classification).
    """
    if target not in df.columns:
        raise KeyError(f"Target '{target}' not in DataFrame columns")
    y = df[target]
    X = df.drop(columns=[target])
    strat = y if stratify else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=strat
    )
    return X_train, X_test, y_train, y_test


def load_from_csv(path: str | Path, **read_kwargs) -> pd.DataFrame:
    """Load training data from a CSV file.

    read_kwargs are passed to pandas.read_csv (e.g., sep, encoding).
    """
    return pd.read_csv(Path(path), **read_kwargs)


def load_from_api(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    json_key: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch JSON from an HTTP API and convert to a DataFrame.

    - If the response JSON is a list, it's treated as records.
    - If it's a dict, set `json_key` to select a list nested under that key.
    """
    import requests

    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        if json_key is not None:
            records = data.get(json_key, [])
        else:
            # Try to find the first list value
            records = next((v for v in data.values() if isinstance(v, list)), [])
    else:
        records = []

    return pd.DataFrame.from_records(records)


def load_from_db(
    connection_url: str,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    coerce_asyncpg: bool = True,
) -> pd.DataFrame:
    """Load data from a SQL database into a DataFrame.

    - `connection_url`: SQLAlchemy URL. If using an async driver like
      `postgresql+asyncpg`, set `coerce_asyncpg=True` to switch to a sync driver
      (`postgresql+psycopg2`) for pandas compatibility.
    - `query`: SQL text to execute.
    - `params`: bound parameters for the query.
    """
    from sqlalchemy import create_engine

    url = connection_url
    if coerce_asyncpg and "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg2")

    engine = create_engine(url)
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df
