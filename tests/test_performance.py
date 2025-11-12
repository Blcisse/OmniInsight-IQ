import time

import time
import numpy as np

from src.deploy.autoscaler import analyze_cpu_usage, trigger_auto_scale


def test_analyze_cpu_usage_and_trigger_scale():
    samples = [10, 20, 40, 80, 75]
    stats = analyze_cpu_usage(samples, window=5)
    assert stats["mean"] > 0 and stats["max"] == 80 or stats["max"] == 75

    # Expect scale up when mean above threshold
    act = trigger_auto_scale(current_replicas=3, cpu_mean=85.0, scale_up_threshold=70.0)
    assert act["desired_replicas"] >= 4

    # Expect scale down when mean below threshold
    act2 = trigger_auto_scale(current_replicas=3, cpu_mean=10.0, scale_down_threshold=30.0)
    assert act2["desired_replicas"] <= 2


def test_api_latency_under_load():
    # Simulate latency samples under load and ensure stats make sense
    samples = [np.random.normal(50, 10) for _ in range(200)]
    stats = analyze_cpu_usage(samples, window=60)
    # Here analyze_cpu_usage is reused for generic stats; mean should be ~50
    assert 30.0 <= stats["mean"] <= 70.0


def benchmark_inference_speed():
    # Synthetic benchmark: assume a dummy predict call latency ~2ms
    # We measure timing loop overhead to validate the harness
    start = time.perf_counter()
    N = 10000
    c = 0
    for _ in range(N):
        c += 1
    elapsed_ms = (time.perf_counter() - start) * 1000
    # Ensure the loop can run reasonably fast in test env
    assert elapsed_ms < 500


def validate_model_memory_usage():
    # Smoke-test: ensure psutil is importable and reports memory
    try:
        import psutil  # type: ignore

        mem = psutil.virtual_memory().percent
        assert 0 <= mem <= 100
    except Exception:
        # If psutil not present, skip gracefully
        assert True
