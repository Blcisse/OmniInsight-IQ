import pandas as pd
import pytest

from src.ai.forecasting.forecast_trainer import train_linear_forecaster
from src.ai.forecasting.forecast_inference import forecast_future


def validate_forecast_accuracy():
    # Simple linear data with slope 2
    df = pd.DataFrame({"date": pd.date_range("2025-01-01", periods=10, freq="D"), "sales": [i * 2 for i in range(10)]})
    model = train_linear_forecaster(df, date_col="date", target_col="sales")
    pred = forecast_future(model, df, date_col="date", horizon_days=5)
    # Last observed value is 18; next value expected close to 20
    assert len(pred) == 5
    assert pred[0]["predicted_sales"] >= 18.5


@pytest.mark.parametrize("horizon", [3, 5])
def test_forecast_trainer_and_inference(horizon):
    df = pd.DataFrame({"date": pd.date_range("2025-01-01", periods=10, freq="D"), "sales": [i * 3 for i in range(10)]})
    model = train_linear_forecaster(df, date_col="date", target_col="sales")
    pred = forecast_future(model, df, date_col="date", horizon_days=horizon)
    assert len(pred) == horizon

