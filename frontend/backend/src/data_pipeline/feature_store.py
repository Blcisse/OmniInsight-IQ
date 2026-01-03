from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import json
import pandas as pd

from .storage_handler import get_postgres_engine, get_redis_client, s3_upload_json


def save_features_to_redis(key: str, df: pd.DataFrame, *, ttl_seconds: Optional[int] = None, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Serialize a DataFrame and store in Redis as JSON under `key`. Optionally sets TTL."""
    r = get_redis_client(redis_url)
    payload = df.to_dict(orient="records")
    r.set(key, json.dumps(payload))
    if ttl_seconds:
        r.expire(key, ttl_seconds)
    return {"key": key, "count": len(payload)}


def load_features_from_redis(key: str, *, redis_url: Optional[str] = None) -> pd.DataFrame:
    r = get_redis_client(redis_url)
    val = r.get(key)
    if not val:
        return pd.DataFrame()
    return pd.DataFrame(json.loads(val))


def save_features_to_postgres(table: str, df: pd.DataFrame, *, if_exists: str = "append", db_url: Optional[str] = None) -> Dict[str, Any]:
    """Save features into a PostgreSQL table via pandas.to_sql.

    Note: For production, consider using proper upserts/transactions.
    """
    eng = get_postgres_engine(db_url)
    with eng.begin() as conn:
        df.to_sql(table, con=conn, if_exists=if_exists, index=False, method="multi")
    return {"table": table, "count": int(len(df))}


def save_features_to_s3(bucket: str, key: str, df: pd.DataFrame, *, s3=None) -> Dict[str, Any]:
    payload = df.to_dict(orient="records")
    return s3_upload_json(bucket, key, payload, s3=s3)


# Simple feature set registry backed by Redis
def _feature_key(name: str) -> str:
    return f"feature_set:{name}"


def register_feature_set(name: str, df: pd.DataFrame, *, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Register a named feature set in Redis as JSON records.

    Overwrites any existing key of the same name. Returns summary.
    """
    r = get_redis_client(redis_url)
    records = df.to_dict(orient="records")
    r.set(_feature_key(name), json.dumps(records))
    return {"name": name, "count": len(records)}


def retrieve_feature_set(name: str, *, redis_url: Optional[str] = None) -> pd.DataFrame:
    """Retrieve a named feature set from Redis as a DataFrame.

    Returns empty DataFrame when not found.
    """
    r = get_redis_client(redis_url)
    raw = r.get(_feature_key(name))
    if not raw:
        return pd.DataFrame()
    return pd.DataFrame(json.loads(raw))


def update_feature_set(name: str, df: pd.DataFrame, *, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Update/replace a stored feature set with new data.

    Same as register_feature_set; provided for explicit intent.
    """
    return register_feature_set(name, df, redis_url=redis_url)
