from __future__ import annotations

from ..core.database import Base

# Import ORM models so that metadata is populated when this package is imported
from .sales import SaleORM  # noqa: F401
from .marketing import CampaignORM, ConversionORM  # noqa: F401
from .products import ProductORM  # noqa: F401
from .user import UserORM  # noqa: F401

__all__ = [
    "Base",
    "SaleORM",
    "CampaignORM",
    "ConversionORM",
    "ProductORM",
    "UserORM",
]

