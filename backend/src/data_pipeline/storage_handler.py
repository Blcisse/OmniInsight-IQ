from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from pathlib import Path


def _coerce_to_sync_driver(url: str) -> str:
    """Ensure SQLAlchemy URL uses a sync driver (e.g., psycopg2) for pandas/SQLAlchemy sync ops."""
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg2")
    return url


def get_postgres_engine(url: Optional[str] = None) -> Engine:
    """Return a synchronous SQLAlchemy Engine for PostgreSQL.

    Prefers `PG_URI` then `DATABASE_URL` from env when `url` is not provided.
    """
    db_url = url or os.getenv("PG_URI") or os.getenv("DATABASE_URL")
    if not db_url:
        # sensible default for local dev
        db_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/omniinsightiq"
    db_url = _coerce_to_sync_driver(db_url)
    return create_engine(db_url, future=True)


def get_redis_client(url: Optional[str] = None):
    """Return a Redis client using `REDIS_URL` or provided url.

    Defers import of redis to avoid hard dependency at import time.
    Returns None if Redis is not available (connection refused, etc.).
    """
    try:
        redis_url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        import redis  # type: ignore
        
        client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except Exception:
        # Redis not available - return None
        return None


def get_s3_client(**kwargs):
    """Return a boto3 S3 client. Credentials are read from env or IAM role.

    Accepts arbitrary boto3 client kwargs for customization.
    """
    import boto3  # type: ignore

    return boto3.client("s3", **kwargs)


def s3_upload_json(bucket: str, key: str, obj: Any, *, s3=None) -> Dict[str, Any]:
    s3 = s3 or get_s3_client()
    body = json.dumps(obj).encode("utf-8")
    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
    return {"bucket": bucket, "key": key}


def s3_download_json(bucket: str, key: str, *, s3=None) -> Any:
    s3 = s3 or get_s3_client()
    resp = s3.get_object(Bucket=bucket, Key=key)
    data = resp["Body"].read()
    return json.loads(data.decode("utf-8"))


# Model artifact helpers in S3
def _models_bucket() -> str:
    bucket = os.getenv("S3_MODELS_BUCKET")
    if not bucket:
        raise RuntimeError("S3_MODELS_BUCKET env var is required for model storage")
    return bucket


def upload_model_to_s3(model_name: str, file_path: str, *, s3=None) -> Dict[str, str]:
    """Upload a local model artifact to S3 under models/<model_name>/<filename>."""
    s3 = s3 or get_s3_client()
    bucket = _models_bucket()
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    key = f"models/{model_name}/{p.name}"
    s3.upload_file(str(p), bucket, key)
    return {"bucket": bucket, "key": key}


def list_s3_models(prefix: str = "models/", *, s3=None) -> Dict[str, Any]:
    """List model artifacts in the S3 models bucket. Returns keys grouped by model."""
    s3 = s3 or get_s3_client()
    bucket = _models_bucket()
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    grouped: Dict[str, list] = {}
    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            parts = key.split("/")
            if len(parts) >= 3 and parts[0] == "models":
                name = parts[1]
                grouped.setdefault(name, []).append(key)
    return grouped


def retrieve_model_from_s3(model_name: str, *, s3=None, dest_dir: Optional[str] = None) -> Dict[str, str]:
    """Download the most recent artifact for the given model into dest_dir (or /tmp).

    Returns { 'bucket', 'key', 'path' } for the downloaded artifact.
    """
    s3 = s3 or get_s3_client()
    bucket = _models_bucket()
    prefix = f"models/{model_name}/"
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = resp.get("Contents", [])
    if not contents:
        raise FileNotFoundError(f"No artifacts for model '{model_name}' under s3://{bucket}/{prefix}")
    # Pick the latest by LastModified
    latest = sorted(contents, key=lambda o: o.get("LastModified"), reverse=True)[0]
    key = latest["Key"]
    out_dir = Path(dest_dir or "/tmp")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / Path(key).name
    s3.download_file(bucket, key, str(dest))
    return {"bucket": bucket, "key": key, "path": str(dest)}


# Redis caching for model predictions
def redis_cache_model_predictions(model_name: str, results: Any, *, ttl_seconds: Optional[int] = None, redis_url: Optional[str] = None) -> Dict[str, Any]:
    r = get_redis_client(redis_url)
    key = f"model_preds:{model_name}"
    r.set(key, json.dumps(results))
    if ttl_seconds is None:
        try:
            ttl_seconds = int(os.getenv("PRED_CACHE_TTL", "0")) or None
        except Exception:
            ttl_seconds = None
    if ttl_seconds:
        r.expire(key, ttl_seconds)
    return {"key": key}


def retrieve_cached_predictions(model_name: str, *, redis_url: Optional[str] = None) -> Any:
    r = get_redis_client(redis_url)
    key = f"model_preds:{model_name}"
    val = r.get(key)
    return json.loads(val) if val else None
