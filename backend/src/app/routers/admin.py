from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..core.database import get_db
from ..models.user import UserORM
from ..models.sales import SaleORM
from .auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin-panel"])


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    users_by_role: dict[str, int]
    total_sales: int
    total_revenue: float


async def require_admin(current_user: Annotated[UserORM, Depends(get_current_user)]) -> UserORM:
    """Dependency to require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard statistics."""
    # User statistics
    total_users_stmt = select(func.count(UserORM.id))
    total_users_result = await db.execute(total_users_stmt)
    total_users = total_users_result.scalar() or 0
    
    active_users_stmt = select(func.count(UserORM.id)).where(UserORM.is_active == True)
    active_users_result = await db.execute(active_users_stmt)
    active_users = active_users_result.scalar() or 0
    
    # Users by role
    users_by_role = {"admin": 0, "analyst": 0, "viewer": 0}
    role_stmt = select(UserORM.role, func.count(UserORM.id)).group_by(UserORM.role)
    role_result = await db.execute(role_stmt)
    for role, count in role_result.all():
        users_by_role[role] = count
    
    # Sales statistics
    try:
        total_sales_stmt = select(func.count(SaleORM.id))
        total_sales_result = await db.execute(total_sales_stmt)
        total_sales = total_sales_result.scalar() or 0
        
        total_revenue_stmt = select(func.sum(SaleORM.revenue))
        total_revenue_result = await db.execute(total_revenue_stmt)
        total_revenue = total_revenue_result.scalar() or 0.0
    except Exception:
        # If sales table doesn't exist or has issues, default to 0
        total_sales = 0
        total_revenue = 0.0
    
    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        users_by_role=users_by_role,
        total_sales=total_sales,
        total_revenue=float(total_revenue) if total_revenue else 0.0,
    )


@router.get("/health")
async def admin_health_check(
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
):
    """Admin health check endpoint."""
    return {
        "status": "ok",
        "admin_user": current_user.username,
        "role": current_user.role,
    }

