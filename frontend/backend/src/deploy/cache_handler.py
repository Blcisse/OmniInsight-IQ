from __future__ import annotations

import json
from typing import Any, Dict, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class CacheHandler:
    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self.url = url
        self._client = redis.from_url(url, decode_responses=True) if redis else None

    def available(self) -> bool:
        return self._client is not None

    def set_json(self, key: str, obj: Any, *, ttl_seconds: Optional[int] = None) -> bool:
        if not self._client:
            return False
        self._client.set(key, json.dumps(obj))
        if ttl_seconds:
            self._client.expire(key, int(ttl_seconds))
        return True

    def get_json(self, key: str) -> Optional[Any]:
        if not self._client:
            return None
        val = self._client.get(key)
        return json.loads(val) if val else None

    def manage_redis_cache_policies(self, *, maxmemory_policy: str = "allkeys-lru") -> bool:
        """Attempt to set Redis maxmemory-policy (requires sufficient permissions).

        Common values: noeviction, allkeys-lru, volatile-ttl, allkeys-random, etc.
        Returns True if command accepted.
        """
        if not self._client:
            return False
        try:
            # CONFIG SET requires proper ACL; ignore failures
            self._client.config_set("maxmemory-policy", maxmemory_policy)
            return True
        except Exception:
            return False

    def purge_stale_entries(self, pattern: str = "*", *, older_than_seconds: Optional[int] = None) -> int:
        """Delete keys matching pattern. If older_than_seconds is provided and Redis supports TTL,
        only deletes keys with small TTL or expired soon (best-effort).
        Returns number of keys deleted.
        """
        if not self._client:
            return 0
        deleted = 0
        try:
            for key in self._client.scan_iter(match=pattern):
                if older_than_seconds is not None:
                    ttl = self._client.ttl(key)
                    if ttl is None or ttl < 0:
                        # No TTL, skip if we only want old keys
                        continue
                    # If key expires within the window, purge it
                    if ttl > older_than_seconds:
                        continue
                try:
                    self._client.delete(key)
                    deleted += 1
                except Exception:
                    continue
        except Exception:
            return deleted
        return deleted

    def compress_cached_payloads(self, pattern: str = "cache:*") -> int:
        """Compress JSON string values under keys matching pattern using gzip.

        Stores compressed bytes under the same key with a prefix marker. Returns number of keys updated.
        """
        import gzip
        if not self._client:
            return 0
        updated = 0
        for key in self._client.scan_iter(match=pattern):
            try:
                val = self._client.get(key)
                if not val or val.startswith("GZ:"):
                    continue
                gz = gzip.compress(val.encode("utf-8"))
                # Prefix marker to distinguish compressed payloads
                blob = b"GZ:" + gz
                # Redis py expects str; store as binary via set(name, value) with decode_responses=False would be ideal,
                # but since client is decode_responses=True, base64 could be used. Keep simple: store hex.
                import base64
                enc = base64.b64encode(blob).decode("ascii")
                self._client.set(key, enc)
                updated += 1
            except Exception:
                continue
        return updated
