from __future__ import annotations

import time
from typing import Any, Callable, Dict, Iterable, Optional, Tuple


class _RateLimiter:
    def __init__(self, rate_per_sec: float, burst: int = 20):
        self.rate = max(0.1, float(rate_per_sec))
        self.capacity = max(1, int(burst))
        self.tokens: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_ts)

    def allow(self, key: str) -> bool:
        now = time.time()
        tokens, last = self.tokens.get(key, (self.capacity, now))
        # refill
        tokens = min(self.capacity, tokens + (now - last) * self.rate)
        allowed = tokens >= 1
        tokens = tokens - 1 if allowed else tokens
        self.tokens[key] = (tokens, now)
        return allowed


def implement_rate_limiting(app, *, rate_per_sec: float = 10.0, burst: int = 20):
    """Install an in-process token-bucket rate limiter keyed by client IP + path.

    For production, prefer an external rate-limiter (NGINX/Envoy/Redis).
    """
    limiter = _RateLimiter(rate_per_sec, burst)

    async def middleware(scope, receive, send):  # type: ignore[override]
        if scope.get("type") != "http":
            return await app(scope, receive, send)
        client = scope.get("client") or ("0.0.0.0", 0)
        ip = client[0]
        path = scope.get("path", "")
        key = f"{ip}:{path}"
        if not limiter.allow(key):
            # 429 Too Many Requests
            await send({"type": "http.response.start", "status": 429, "headers": [(b"content-type", b"application/json")]})
            await send({"type": "http.response.body", "body": b'{"detail":"rate limit exceeded"}'})
            return
        return await app(scope, receive, send)

    return middleware


def detect_brute_force_patterns(attempts: Iterable[Dict[str, Any]], *, window_seconds: int = 300, threshold: int = 10) -> Dict[str, Any]:
    """Analyze auth attempts for brute-force patterns per IP/username.

    attempts: iterable of { ts: epoch_sec, ip: str, user: str, success: bool }
    Returns offenders with counts in the window and a simple score.
    """
    now = time.time()
    offenders: Dict[str, int] = {}
    for a in attempts:
        try:
            if not a.get("success") and now - float(a.get("ts", now)) <= window_seconds:
                key = f"{a.get('ip','?')}:{a.get('user','?')}"
                offenders[key] = offenders.get(key, 0) + 1
        except Exception:
            continue
    flagged = {k: v for k, v in offenders.items() if v >= threshold}
    return {"flagged": flagged, "total_failed": sum(offenders.values())}


def enable_request_throttling(app, *, rate_per_sec: float = 50.0, burst: int = 100):
    """Shorthand to install the rate limiter across all routes."""
    return implement_rate_limiting(app, rate_per_sec=rate_per_sec, burst=burst)

