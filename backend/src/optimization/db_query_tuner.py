from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, selectinload, joinedload


def _to_session(engine_or_session: Any) -> Tuple[Optional[Session], Optional[Engine]]:
    if isinstance(engine_or_session, Session):
        return engine_or_session, None
    return None, engine_or_session


def analyze_query_latency(engine_or_session: Any, sql: str, *, params: Optional[Dict[str, Any]] = None, samples: int = 3) -> Dict[str, Any]:
    """Execute a raw SQL statement multiple times and report latency stats (ms)."""
    times: List[float] = []
    sess, eng = _to_session(engine_or_session)
    for _ in range(max(1, samples)):
        t0 = time.perf_counter()
        if sess is not None:
            sess.execute(text(sql), params or {})
        else:
            assert eng is not None
            with eng.connect() as conn:
                conn.execute(text(sql), params or {})
        times.append((time.perf_counter() - t0) * 1000.0)
    return {"runs": len(times), "min_ms": min(times), "max_ms": max(times), "avg_ms": sum(times) / len(times)}


def batch_query_execution(engine_or_session: Any, statements: Iterable[Tuple[str, Optional[Dict[str, Any]]]]) -> List[int]:
    """Execute multiple SQL statements in a single transaction; return rowcount per statement.

    statements: iterable of (sql, params)
    """
    sess, eng = _to_session(engine_or_session)
    results: List[int] = []
    if sess is not None:
        with sess.begin():
            for sql, params in statements:
                res = sess.execute(text(sql), params or {})
                results.append(getattr(res, "rowcount", -1))
        return results
    assert eng is not None
    with eng.begin() as conn:
        for sql, params in statements:
            res = conn.execute(text(sql), params or {})
            results.append(getattr(res, "rowcount", -1))
    return results


def optimize_joins(query, *, strategy: str = "selectin", relationships: Optional[Iterable[Any]] = None):
    """Apply eager loading strategy to ORM query to reduce N+1 problems.

    - strategy: 'selectin' (default) or 'joined'
    - relationships: iterable of relationship attributes, e.g., Model.rel
    Returns a modified query when possible, otherwise the original query.
    """
    if relationships is None:
        return query
    try:
        if strategy == "joined":
            for rel in relationships:
                query = query.options(joinedload(rel))
        else:
            for rel in relationships:
                query = query.options(selectinload(rel))
        return query
    except Exception:
        return query

