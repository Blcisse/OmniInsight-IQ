"""
Seed script to create default development users.
Only runs in development/test environments.
"""
from __future__ import annotations

import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from .security import get_password_hash
from ..models.user import UserORM


async def create_default_user(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123",
    role: str = "admin",
) -> UserORM | None:
    """Create a default user if it doesn't exist. Returns the user or None."""
    async with AsyncSessionLocal() as db:
        # Check if user already exists
        stmt = select(UserORM).where(UserORM.username == username)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return existing_user
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = UserORM(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


async def seed_development_users():
    """Seed development users. Only runs if ENABLE_DEV_SEED is true."""
    if os.getenv("ENABLE_DEV_SEED", "false").lower() not in {"1", "true", "yes"}:
        return
    
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "development"))
    if env.lower() == "production":
        print("⚠ Skipping seed: Production environment detected")
        return
    
    print("🌱 Seeding development users...")
    
    # Create admin user
    admin = await create_default_user(
        username=os.getenv("DEV_ADMIN_USERNAME", "admin"),
        email=os.getenv("DEV_ADMIN_EMAIL", "admin@example.com"),
        password=os.getenv("DEV_ADMIN_PASSWORD", "admin123"),
        role="admin",
    )
    if admin:
        print(f"✓ Created/Found admin user: {admin.username}")
    
    # Create analyst user
    analyst = await create_default_user(
        username=os.getenv("DEV_ANALYST_USERNAME", "analyst"),
        email=os.getenv("DEV_ANALYST_EMAIL", "analyst@example.com"),
        password=os.getenv("DEV_ANALYST_PASSWORD", "analyst123"),
        role="analyst",
    )
    if analyst:
        print(f"✓ Created/Found analyst user: {analyst.username}")
    
    print("✓ Seed complete")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_development_users())

