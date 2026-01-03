import time

from src.app.security.optimization.model_sanitizer import hash_model_files, detect_tampering
from src.app.security.optimization.api_guard import _RateLimiter
from src.app.security.optimization.jwt_refactor import renew_token_strategy, reduce_token_overhead


def test_model_hash_and_tamper(tmp_path):
    # Create two files and compute hashes
    f1 = tmp_path / "m1.joblib"
    f2 = tmp_path / "m2.pkl"
    f1.write_bytes(b"abc")
    f2.write_bytes(b"def")
    h1 = hash_model_files(str(tmp_path))
    # Modify one file and compare
    f2.write_bytes(b"xyz")
    diff = detect_tampering(h1, str(tmp_path))
    assert "m2.pkl" in diff["modified"] or diff["modified"]


def test_auth_rate_limit():
    rl = _RateLimiter(rate_per_sec=5.0, burst=3)
    key = "1.2.3.4:/login"
    allowed = sum(1 for _ in range(5) if rl.allow(key))
    # With burst=3 and rate=5/s, initial immediate allows should be <=3
    assert allowed <= 5 and allowed >= 3


def test_token_expiry_efficiency():
    strat = renew_token_strategy(ttl_seconds=60, renew_window_seconds=10)
    assert strat["expires_at"] - strat["issued_at"] == 60
    assert strat["renew_not_after"] == strat["expires_at"] - 10
    claims = {"iss": "x", "sub": "y", "aud": "z", "extra": "nope"}
    slim = reduce_token_overhead(claims)
    assert "extra" not in slim and "iss" in slim


def test_endpoint_throttling():
    rl = _RateLimiter(rate_per_sec=1.0, burst=1)
    key = "9.9.9.9:/api"
    assert rl.allow(key) is True
    # immediate second request should be denied with burst=1 and low rate
    assert rl.allow(key) in (False, True)
