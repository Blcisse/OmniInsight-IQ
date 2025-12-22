import pytest
from sqlalchemy import text
from src.app.core.database import AsyncSessionLocal
from src.app.models import SaleORM, CampaignORM
from src.app.lib.mlModels.regressionModel import linear_regression_forecast
from src.app.lib.mlModels.clusteringModel import kmeans_segments

pytestmark = pytest.mark.integration

@pytest.mark.asyncio
async def test_regression_forecast_shape_and_nonnegative(db_setup):
    async with AsyncSessionLocal() as session:
        # Clear table safely
        await session.execute(text("TRUNCATE TABLE sales RESTART IDENTITY CASCADE;"))
        await session.commit()

        # Seed minimal series
        session.add_all([
            SaleORM(product_id="p1", date="2025-11-01", region="NA", units_sold=2, revenue=100.0),
            SaleORM(product_id="p1", date="2025-11-02", region="NA", units_sold=3, revenue=115.0),
            SaleORM(product_id="p1", date="2025-11-03", region="NA", units_sold=4, revenue=130.0),
        ])
        await session.commit()

        forecast = await linear_regression_forecast(session, horizon_days=5)

    assert len(forecast) == 5
    for f in forecast:
        assert "date" in f and "predicted_sales" in f
        assert isinstance(f["predicted_sales"], (int, float))
        assert f["predicted_sales"] >= 0

@pytest.mark.asyncio
async def test_kmeans_clusters_returned(db_setup):
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE campaigns RESTART IDENTITY CASCADE;"))
        await session.commit()

        # Seed campaigns
        session.add_all([
            CampaignORM(campaign_name="C1", channel="Search", budget=100, spend=50, impressions=1000, clicks=50, roi=2.0),
            CampaignORM(campaign_name="C2", channel="Social", budget=200, spend=150, impressions=5000, clicks=400, roi=3.5),
            CampaignORM(campaign_name="C3", channel="Email", budget=50, spend=20, impressions=800, clicks=120, roi=4.2),
        ])
        await session.commit()

        clusters = await kmeans_segments(session, n_clusters=2, entity="campaign")

    assert isinstance(clusters, list)
    assert len(clusters) >= 1
    for c in clusters:
        assert "cluster" in c and "size" in c and "centroid" in c and "members" in c
        assert c["size"] >= 1
