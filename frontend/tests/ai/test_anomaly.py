import pandas as pd
from src.ai.anomaly_detection.anomaly_detector import detect_statistical_zscore, detect_anomalies


def test_anomaly_detection_precision():
    # Construct a series with clear outliers
    vals = [10] * 20 + [200, 250]
    s = pd.Series(vals)
    res = detect_statistical_zscore(s, threshold=3.0)
    anomalies = res[res["is_anomaly"]]
    # Expect at least the last two to be flagged
    assert anomalies.shape[0] >= 2


def test_detect_anomalies_dataframe():
    df = pd.DataFrame({"a": [1, 1, 1, 100], "b": [2, 2, 2, 200]})
    out = detect_anomalies(df, threshold=2.0)
    assert "score" in out.columns and "is_anomaly" in out.columns

