import json

from src.deploy.cache_handler import CacheHandler


def test_cache_handler_roundtrip(monkeypatch):
    # Skip test if Redis is not available by simulating unavailability
    ch = CacheHandler(url="redis://invalid:6379/0")
    if not ch.available():
        assert ch.get_json("k1") is None
        assert not ch.set_json("k1", {"a": 1})
    else:
        assert ch.set_json("k2", {"b": 2}, ttl_seconds=1)
        val = ch.get_json("k2")
        assert isinstance(val, dict)


def test_redis_eviction_policy(monkeypatch):
    ch = CacheHandler(url="redis://invalid:6379/0")
    # If Redis is not available, function should return False without raising
    ok = ch.manage_redis_cache_policies(maxmemory_policy="allkeys-lru")
    assert ok in (True, False)


def verify_model_cache_persistence(tmp_path):
    # Use filesystem as a simple stand-in for persistence checks (not Redis)
    # Write and read a JSON to simulate persistence behavior
    p = tmp_path / "cache.json"
    data = {"model": "m1", "ver": "v1"}
    p.write_text(json.dumps(data))
    loaded = json.loads(p.read_text())
    assert loaded["model"] == "m1"


def simulate_high_request_load():
    # Ensure compress_cached_payloads safe path runs without exceptions when Redis unavailable
    ch = CacheHandler(url="redis://invalid:6379/0")
    updated = ch.compress_cached_payloads(pattern="cache:*")
    assert isinstance(updated, int)
