"""
Tests for Forecasting Router with Real Data
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.main import app

client = TestClient(app)


class TestForecastingMetrics:
    """Test forecast metrics endpoint"""
    
    def test_get_metrics_default_horizon(self):
        """Test getting metrics with default horizon"""
        response = client.get("/api/forecasting/metrics")
        assert response.status_code == 200
        data = response.json()
        
        assert "totalForecastedRevenue" in data
        assert "forecastedGrowth" in data
        assert "confidence" in data
        assert "horizon" in data
        assert "lastUpdated" in data
        
        assert data["horizon"] == 30
        assert data["totalForecastedRevenue"] > 0
        assert data["confidence"] > 0
    
    def test_get_metrics_custom_horizon(self):
        """Test getting metrics with custom horizon"""
        response = client.get("/api/forecasting/metrics?horizon=60")
        assert response.status_code == 200
        data = response.json()
        assert data["horizon"] == 60
    
    def test_get_metrics_invalid_horizon_too_low(self):
        """Test metrics with horizon below minimum"""
        response = client.get("/api/forecasting/metrics?horizon=5")
        assert response.status_code == 422
    
    def test_get_metrics_invalid_horizon_too_high(self):
        """Test metrics with horizon above maximum"""
        response = client.get("/api/forecasting/metrics?horizon=400")
        assert response.status_code == 422


class TestProductForecast:
    """Test product forecast endpoints"""
    
    def test_get_product_forecast_default(self):
        """Test getting forecast for a product"""
        response = client.get("/api/forecasting/products/prod_001")
        assert response.status_code == 200
        data = response.json()
        
        assert "productId" in data
        assert "productName" in data
        assert "forecast" in data
        assert "accuracy" in data
        assert len(data["forecast"]) == 30
        assert 0 <= data["accuracy"] <= 1
    
    def test_get_product_forecast_custom_horizon(self):
        """Test getting forecast with custom horizon"""
        response = client.get("/api/forecasting/products/prod_002?horizon=14")
        assert response.status_code == 200
        data = response.json()
        assert len(data["forecast"]) == 14
    
    def test_forecast_point_structure(self):
        """Test structure of forecast points"""
        response = client.get("/api/forecasting/products/prod_003")
        assert response.status_code == 200
        data = response.json()
        
        forecast_point = data["forecast"][0]
        assert "date" in forecast_point
        assert "value" in forecast_point
        assert "confidence_lower" in forecast_point
        assert "confidence_upper" in forecast_point
        
        # Verify confidence intervals
        assert forecast_point["confidence_lower"] < forecast_point["value"]
        assert forecast_point["confidence_upper"] > forecast_point["value"]


class TestBatchForecast:
    """Test batch forecast endpoint"""
    
    def test_batch_forecast_multiple_products(self):
        """Test getting forecasts for multiple products"""
        product_ids = ["prod_001", "prod_002", "prod_003"]
        response = client.post(
            "/api/forecasting/products/batch",
            json=product_ids
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_batch_forecast_custom_horizon(self):
        """Test batch forecast with custom horizon"""
        product_ids = ["prod_001", "prod_002"]
        response = client.post(
            "/api/forecasting/products/batch?horizon=21",
            json=product_ids
        )
        assert response.status_code == 200
        data = response.json()
        assert all(len(item["forecast"]) == 21 for item in data)
    
    def test_batch_forecast_empty_list(self):
        """Test batch forecast with empty product list"""
        response = client.post(
            "/api/forecasting/products/batch",
            json=[]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestRealDataIntegration:
    """Test integration with real RavenStack/Chioma data"""
    
    def test_metrics_uses_real_sales_data(self):
        """Verify metrics endpoint loads real sales funnel data"""
        response = client.get("/api/forecasting/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Should have positive revenue from real data
        assert data["totalForecastedRevenue"] > 0
        print(f"Total Forecasted Revenue: ${data['totalForecastedRevenue']:,.2f}")
    
    def test_date_formats_are_valid(self):
        """Test that all dates are valid ISO format"""
        response = client.get("/api/forecasting/products/test_prod")
        assert response.status_code == 200
        data = response.json()
        
        for point in data["forecast"]:
            # Should parse without error
            datetime.fromisoformat(point["date"])