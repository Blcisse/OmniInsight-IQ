import pytest

def test_forecasting_endpoint():
    response = client.get('/forecasting')
    assert response.status_code == 200
    assert 'forecast' in response.json()