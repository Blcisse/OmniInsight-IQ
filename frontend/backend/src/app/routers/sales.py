from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.sales import SaleORM


router = APIRouter(prefix="/api/sales", tags=["sales"])


class Sale(BaseModel):
    id: int
    product_id: str
    date: str
    region: Optional[str] = None
    units_sold: int
    revenue: float
    profit_margin: Optional[float] = None


@router.get("/", response_model=List[Sale])
async def list_sales(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[Sale]:
    stmt = select(SaleORM)
    conditions = []
    if start_date:
        conditions.append(SaleORM.date >= start_date)
    if end_date:
        conditions.append(SaleORM.date <= end_date)
    if region:
        conditions.append(SaleORM.region == region)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(SaleORM.date.desc()).limit(limit).offset(offset)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [
        Sale(
            id=r.id,
            product_id=r.product_id,
            date=r.date,
            region=r.region,
            units_sold=r.units_sold,
            revenue=r.revenue,
            profit_margin=r.profit_margin,
        )
        for r in rows
    ]


@router.get("/{sale_id}", response_model=Sale)
async def get_sale(sale_id: int, db: AsyncSession = Depends(get_db)) -> Sale:
    stmt = select(SaleORM).where(SaleORM.id == sale_id)
    res = await db.execute(stmt)
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Sale not found")
    return Sale(
        id=r.id,
        product_id=r.product_id,
        date=r.date,
        region=r.region,
        units_sold=r.units_sold,
        revenue=r.revenue,
        profit_margin=r.profit_margin,
    )


class NewSale(BaseModel):
    product_id: str
    date: str
    region: Optional[str] = None
    units_sold: int
    revenue: float
    profit_margin: Optional[float] = None


@router.post("/", response_model=Sale, status_code=201)
async def create_sale(payload: NewSale, db: AsyncSession = Depends(get_db)) -> Sale:
    stmt = (
        insert(SaleORM)
        .values(
            product_id=payload.product_id,
            date=payload.date,
            region=payload.region,
            units_sold=payload.units_sold,
            revenue=payload.revenue,
            profit_margin=payload.profit_margin,
        )
        .returning(SaleORM)
    )
    res = await db.execute(stmt)
    await db.commit()
    r = res.scalar_one()
    return Sale(
        id=r.id,
        product_id=r.product_id,
        date=r.date,
        region=r.region,
        units_sold=r.units_sold,
        revenue=r.revenue,
        profit_margin=r.profit_margin,
    )
