"""
Forecasting Router
Provides endpoints for time series forecasting and metrics
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/forecasting", tags=["forecasting"])


# Models
class ForecastPoint(BaseModel):
    date: str
    value: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None


class ProductForecast(BaseModel):
    productId: str
    productName: str
    forecast: List[ForecastPoint]
    accuracy: Optional[float] = None
    model: str = "arima"


class ForecastMetrics(BaseModel):
    totalForecastedRevenue: float
    forecastedGrowth: float
    confidence: float
    horizon: int
    lastUpdated: str


# Mock data generators
def generate_mock_forecast(product_id: str, product_name: str, horizon: int = 30) -> ProductForecast:
    """Generate mock forecast data for a product"""
    import random
    base_date = datetime.now()
    forecast_points = []
    
    base_value = random.uniform(1000, 5000)
    for i in range(horizon):
        date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        value = base_value * (1 + random.uniform(-0.1, 0.15))
        confidence_lower = value * 0.85
        confidence_upper = value * 1.15
        
        forecast_points.append(
            ForecastPoint(
                date=date,
                value=round(value, 2),
                confidence_lower=round(confidence_lower, 2),
                confidence_upper=round(confidence_upper, 2),
            )
        )
        base_value = value  # Trend continues
    
    return ProductForecast(
        productId=product_id,
        productName=product_name,
        forecast=forecast_points,
        accuracy=random.uniform(0.75, 0.95),
        model="arima",
    )


def get_mock_metrics(horizon: int = 30) -> ForecastMetrics:
    """Generate mock forecast metrics"""
    import random
    return ForecastMetrics(
        totalForecastedRevenue=round(random.uniform(500000, 1000000), 2),
        forecastedGrowth=round(random.uniform(0.05, 0.25), 3),
        confidence=round(random.uniform(0.80, 0.95), 3),
        horizon=horizon,
        lastUpdated=datetime.now().isoformat(),
    )


# Endpoints
@router.get("/metrics", response_model=ForecastMetrics)
async def get_forecast_metrics(horizon: int = Query(30, ge=7, le=365)):
    """Get overall forecast metrics"""
    return get_mock_metrics(horizon)


@router.get("/products/{product_id}", response_model=ProductForecast)
async def get_product_forecast(
    product_id: str,
    horizon: int = Query(30, ge=7, le=365),
):
    """Get forecast for a specific product"""
    product_names = {
        "prod_001": "Premium Organic Blend",
        "prod_002": "Energy Boost Formula",
        "prod_003": "Wellness Essentials",
        "prod_004": "Daily Nutrition Pack",
        "prod_005": "Performance Plus",
    }
    product_name = product_names.get(product_id, f"Product {product_id}")
    return generate_mock_forecast(product_id, product_name, horizon)


@router.post("/products/batch", response_model=List[ProductForecast])
async def get_multiple_forecasts(
    product_ids: List[str],
    horizon: int = Query(30, ge=7, le=365),
):
    """Get forecasts for multiple products"""
    product_names = {
        "prod_001": "Premium Organic Blend",
        "prod_002": "Energy Boost Formula",
        "prod_003": "Wellness Essentials",
        "prod_004": "Daily Nutrition Pack",
        "prod_005": "Performance Plus",
    }
    
    forecasts = []
    for pid in product_ids[:10]:  # Limit to 10 products
        product_name = product_names.get(pid, f"Product {pid}")
        forecasts.append(generate_mock_forecast(pid, product_name, horizon))
    
    return forecasts
