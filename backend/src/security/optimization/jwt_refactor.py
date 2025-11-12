from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Optional, Tuple


def renew_token_strategy(
    *,
    ttl_seconds: int = 3600,
    renew_window_seconds: int = 300,
    clock_skew_seconds: int = 30,
) -> Dict[str, Any]:
    """Return a strategy for JWT renewal with proactive refresh.

    - ttl_seconds: token lifetime
    - renew_window_seconds: time before expiry to proactively renew
    - clock_skew_seconds: allowed leeway for clock skew

    Example client logic with JWT `exp`:
      if now >= exp - renew_window: refresh()
    """
    now = int(time.time())
    exp = now + int(ttl_seconds)
    renew_at = exp - int(renew_window_seconds)
    return {
        "issued_at": now,
        "expires_at": exp,
        "renew_not_after": renew_at,
        "clock_skew": int(clock_skew_seconds),
    }


def reduce_token_overhead(
    claims: Dict[str, Any],
    *,
    keep: Optional[Iterable[str]] = None,
    alias_map: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Trim non-essential claims and optionally alias keys to shorter names.

    - keep: explicit list of claims to preserve; defaults to registered claims
    - alias_map: mapping from long -> short keys (e.g., {'subject': 'sub'})
    """
    default_keep = {"iss", "sub", "aud", "exp", "iat", "nbf", "jti"}
    keep_set = set(keep) if keep is not None else default_keep
    slim = {k: v for k, v in claims.items() if k in keep_set}
    if alias_map:
        slim = {alias_map.get(k, k): v for k, v in slim.items()}
    return slim


def optimize_auth_middleware(
    app,
    *,
    header: str = "authorization",
    cache_ttl: int = 60,
):
    """Wrap an ASGI app with a micro JWT cache to reduce repeated verification.

    NOTE: This is a lightweight illustration; for production use a shared cache (e.g., Redis)
    and robust verification. The middleware caches tokens per-process for `cache_ttl` seconds.
    """
    cache: Dict[str, Tuple[int, bool]] = {}

    async def middleware(scope, receive, send):  # type: ignore[override]
        if scope.get("type") != "http":
            return await app(scope, receive, send)
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        token = headers.get(header)
        now = int(time.time())
        if token:
            entry = cache.get(token)
            if entry and now - entry[0] < cache_ttl:
                # short-circuit; pretend verified
                return await app(scope, receive, send)
            # In a real system verify signature/claims here; we assume ok
            cache[token] = (now, True)
        return await app(scope, receive, send)

    return middleware

