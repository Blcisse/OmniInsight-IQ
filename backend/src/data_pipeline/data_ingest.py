from __future__ import annotations

from typing import Any, Dict, Optional

import os
import pandas as pd
from sqlalchemy import text

from .storage_handler import get_postgres_engine, s3_download_json


def fetch_sales_data(limit: Optional[int] = None, *, db_url: Optional[str] = None) -> pd.DataFrame:
    """Fetch sales data from PostgreSQL `sales` table.

    Returns a DataFrame with the latest rows ordered by date desc.
    """
    eng = get_postgres_engine(db_url)
    query = "SELECT * FROM sales ORDER BY date DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    with eng.connect() as conn:
        df = pd.read_sql_query(text(query), conn)
    return df


def fetch_health_data(limit: Optional[int] = None, *, db_url: Optional[str] = None) -> pd.DataFrame:
    """Fetch platform or application health metrics if available.

    Attempts to read from a `health_metrics` table; returns empty DataFrame if not present.
    """
    eng = get_postgres_engine(db_url)
    table = "health_metrics"
    query = f"SELECT * FROM {table} ORDER BY timestamp DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    try:
        with eng.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        return df
    except Exception:
        return pd.DataFrame()


def sync_external_sources(
    *,
    s3_bucket: Optional[str] = None,
    s3_key: Optional[str] = None,
    target_table: str = "external_data",
    db_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Download external dataset from S3 (JSON records) and sync into PostgreSQL.

    Creates/appends to `target_table`. Returns a summary dict.
    """
    if not s3_bucket or not s3_key:
        # read defaults from env for convenience
        s3_bucket = s3_bucket or os.getenv("S3_INGEST_BUCKET")
        s3_key = s3_key or os.getenv("S3_INGEST_KEY")
    if not s3_bucket or not s3_key:
        raise ValueError("s3_bucket and s3_key are required for sync_external_sources")

    payload = s3_download_json(s3_bucket, s3_key)
    if not isinstance(payload, list):
        raise ValueError("Expected list of records in S3 JSON payload")

    df = pd.DataFrame.from_records(payload)
    if df.empty:
        return {"bucket": s3_bucket, "key": s3_key, "table": target_table, "count": 0}

    eng = get_postgres_engine(db_url)
    with eng.begin() as conn:
        df.to_sql(target_table, con=conn, if_exists="append", index=False, method="multi")
    return {"bucket": s3_bucket, "key": s3_key, "table": target_table, "count": int(len(df))}

