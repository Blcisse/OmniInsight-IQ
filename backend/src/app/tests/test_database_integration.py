import asyncio
import os
import pytest
from sqlalchemy import select, text

from src.app.core.database import engine, AsyncSessionLocal
from src.app.models import Base, ProductORM, SaleORM, CampaignORM


@pytest.mark.asyncio
async def test_crud_sales_and_queries(db_setup):
    # Insert a product and sales rows
    async with AsyncSessionLocal() as session:
        # Ensure clean slate
        await session.execute(text("DELETE FROM sales"))
        await session.execute(text("DELETE FROM products"))
        await session.commit()

        p = ProductORM(name="Test Product", category="Widgets", price=9.99, stock=100)
        session.add(p)
        await session.flush()

        s1 = SaleORM(product_id=str(p.id), date="2025-11-01", region="NA", units_sold=5, revenue=49.95, profit_margin=25.0)
        s2 = SaleORM(product_id=str(p.id), date="2025-11-02", region="EU", units_sold=3, revenue=29.97, profit_margin=22.0)
        session.add_all([s1, s2])
        await session.commit()

    # Query and assert aggregates
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(SaleORM))
        rows = res.scalars().all()
        assert len(rows) == 2

        total_rev = sum(r.revenue for r in rows)
        assert pytest.approx(total_rev, rel=1e-6) == 79.92

        # Filter by date
        res2 = await session.execute(select(SaleORM).where(SaleORM.date >= "2025-11-02"))
        rows2 = res2.scalars().all()
        assert len(rows2) == 1


@pytest.mark.asyncio
async def test_campaign_crud(db_setup):
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM campaigns"))
        await session.commit()

        c = CampaignORM(campaign_name="Black Friday", channel="Search", budget=1000.0, spend=250.0, impressions=10000, clicks=500, roi=3.2)
        session.add(c)
        await session.commit()

        res = await session.execute(select(CampaignORM))
        rows = res.scalars().all()
        assert len(rows) == 1
        assert rows[0].campaign_name == "Black Friday"

