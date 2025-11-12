from __future__ import annotations

import asyncio
from datetime import date, timedelta

from sqlalchemy import text

from src.app.core.database import AsyncSessionLocal, engine
from src.app.core.database import create_all_tables
from src.app.models import SaleORM, CampaignORM
from src.app.lib.mlModels.regressionModel import linear_regression_forecast
from src.app.lib.mlModels.clusteringModel import kmeans_segments


async def main() -> None:
    # Ensure schema exists
    await create_all_tables()

    # Clean target tables using a dedicated engine transaction
    async with engine.begin() as conn:
        try:
            await conn.execute(text("TRUNCATE TABLE sales RESTART IDENTITY CASCADE"))
        except Exception:
            pass
        try:
            await conn.execute(text("TRUNCATE TABLE campaigns RESTART IDENTITY CASCADE"))
        except Exception:
            pass

    # Seed minimal data and run predictions
    async with AsyncSessionLocal() as session:
        # Seed 7 days of simple increasing sales for one product
        base = date.today() - timedelta(days=6)
        sales = []
        for i in range(7):
            d = base + timedelta(days=i)
            sales.append(
                SaleORM(
                    product_id="p1",
                    date=str(d),
                    region="NA",
                    units_sold=2 + i,  # 2..8
                    revenue=100.0 + 15 * i,
                )
            )
        session.add_all(sales)

        # Seed a few campaigns with distinct budgets/spend/clicks for clustering
        campaigns = [
            CampaignORM(campaign_name="C1", channel="Search", budget=100, spend=50, impressions=1000, clicks=50, roi=2.0),
            CampaignORM(campaign_name="C2", channel="Social", budget=200, spend=150, impressions=5000, clicks=400, roi=3.5),
            CampaignORM(campaign_name="C3", channel="Email", budget=50, spend=20, impressions=800, clicks=120, roi=4.2),
        ]
        session.add_all(campaigns)
        await session.commit()

        # Run forecast for next 5 days
        forecast = await linear_regression_forecast(session, horizon_days=5)
        print("Forecast (next 5 days):")
        for f in forecast:
            print(f)

        # Run simple kmeans clustering over campaigns
        clusters = await kmeans_segments(session, n_clusters=2, entity="campaign")
        print("\nCampaign clusters (k=2):")
        for c in clusters:
            print(c)


if __name__ == "__main__":
    asyncio.run(main())

