from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union


def optimize_api_response(
    data: Union[List[Dict[str, Any]], Dict[str, Any]],
    *,
    fields: Optional[Iterable[str]] = None,
    limit: Optional[int] = None,
    sort_by: Optional[str] = None,
    reverse: bool = False,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Trim payload size by field selection, sorting and limiting.

    - data: list of dicts or a dict
    - fields: if provided, only keep these keys in dict items
    - sort_by: key to sort a list of dicts by
    - limit: truncate list to first N items
    Returns the optimized payload (same shape as input where possible).
    """
    if not isinstance(data, list):
        if fields and isinstance(data, dict):
            return {k: v for k, v in data.items() if k in set(fields)}
        return data

    items = data
    if fields:
        keep = set(fields)
        items = [{k: v for k, v in row.items() if k in keep} for row in items]
    if sort_by:
        try:
            items = sorted(items, key=lambda r: r.get(sort_by), reverse=reverse)
        except Exception:
            pass
    if limit is not None:
        items = items[: int(limit)]
    return items


def compress_payload(
    payload: Union[bytes, str, Dict[str, Any], List[Any]],
    *,
    algorithm: str = "gzip",
) -> Tuple[bytes, Dict[str, str]]:
    """Compress a payload and return (content, headers) for HTTP response.

    - algorithm: 'gzip' or 'br' (brotli if installed)
    """
    raw: bytes
    if isinstance(payload, bytes):
        raw = payload
    elif isinstance(payload, str):
        raw = payload.encode("utf-8")
    else:
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    algo = algorithm.lower()
    if algo in {"br", "brotli"}:
        try:
            import brotli  # type: ignore

            out = brotli.compress(raw)
            return out, {"Content-Encoding": "br"}
        except Exception:
            # fallback to gzip
            algo = "gzip"

    if algo == "gzip":
        import gzip

        out = gzip.compress(raw)
        return out, {"Content-Encoding": "gzip"}

    # no compression
    return raw, {}


class _TTLCacheMiddleware:
    """Very small in-process TTL cache for GET routes.

    Not production-grade; use an external cache (e.g., CDN/NGINX/Redis) for scale.
    """

    def __init__(self, app, routes: Iterable[str], ttl_seconds: int = 300) -> None:
        self.app = app
        self.routes = set(routes)
        self.ttl = ttl_seconds
        self.cache: Dict[str, Tuple[float, bytes, list[tuple[str, str]]]] = {}

    async def __call__(self, scope, receive, send):  # type: ignore[override]
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path", "")
        method = scope.get("method", "").upper()
        if method == "GET" and path in self.routes:
            entry = self.cache.get(path)
            now = time.time()
            if entry and now - entry[0] < self.ttl:
                body = entry[1]
                headers = entry[2]

                async def cached_send(message):
                    if message["type"] == "http.response.start":
                        # Merge cached headers
                        message.setdefault("headers", [])
                        message["headers"].extend(
                            [(k.encode(), v.encode()) for k, v in headers]
                        )
                    if message["type"] == "http.response.body":
                        message["body"] = body
                    await send(message)

                return await cached_send({"type": "http.response.start", "status": 200})

            # Capture downstream response
            captured: Dict[str, Any] = {"body": b"", "headers": [], "status": 200}

            async def caching_send(message):
                if message["type"] == "http.response.start":
                    captured["status"] = message.get("status", 200)
                    hdrs = message.get("headers") or []
                    captured["headers"] = [(k.decode(), v.decode()) for k, v in hdrs]
                if message["type"] == "http.response.body":
                    captured["body"] = message.get("body", b"")
                await send(message)

            await self.app(scope, receive, caching_send)
            if captured["status"] == 200:
                self.cache[path] = (now, captured["body"], captured["headers"])
            return

        return await self.app(scope, receive, send)


def cache_static_routes(app, routes: Iterable[str], ttl_seconds: int = 300) -> None:
    """Install a simple in-process TTL cache for a set of GET routes."""
    app.add_middleware(type("TTLCacheMW", (), {"__call__": _TTLCacheMiddleware(app, routes, ttl_seconds).__call__}))

