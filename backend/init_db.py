"""Initialize InsightOps database with tables and seed data"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.app.models.insightops import Base, IoKpiDailyORM, IoEngagementSignalDailyORM
from datetime import date, timedelta
import random

DATABASE_URL = "postgresql+asyncpg://localhost/omniinsightiq"

async def init_database():
    """Create all tables and seed initial data"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created!")
    
    # Seed sample data
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Seed KPI data (revenue)
        today = date.today()
        for i in range(30):
            kpi_date = today - timedelta(days=i)
            revenue = 50000 + random.uniform(-5000, 10000)
            
            kpi = IoKpiDailyORM(
                kpi_date=kpi_date,
                org_id="demo_org",
                metric_key="revenue",
                metric_value=revenue,
                metric_unit="USD",
                source="seed_data"
            )
            session.add(kpi)
        
        # Seed engagement data (touches)
        for i in range(30):
            signal_date = today - timedelta(days=i)
            touches = 100 + random.uniform(-20, 40)
            
            signal = IoEngagementSignalDailyORM(
                signal_date=signal_date,
                org_id="demo_org",
                signal_key="touches",
                signal_value=touches,
                source="seed_data"
            )
            session.add(signal)
        
        await session.commit()
    
    print("✅ Sample data seeded!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())