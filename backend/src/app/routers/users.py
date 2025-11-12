from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from ..core.database import get_db
from ..core.security import get_password_hash, verify_password
from ..models.user import UserORM
from .auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["user-management"])


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "viewer"
    is_active: bool = True


async def require_admin(current_user: Annotated[UserORM, Depends(get_current_user)]) -> UserORM:
    """Dependency to require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all users (admin only)."""
    stmt = select(UserORM).offset(skip).limit(limit).order_by(UserORM.id)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        role=u.role,
    ) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user by ID (admin only)."""
    stmt = select(UserORM).where(UserORM.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user (admin only)."""
    # Check if username exists
    stmt = select(UserORM).where(UserORM.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    # Check if email exists
    stmt = select(UserORM).where(UserORM.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    
    # Validate role
    if user_data.role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be one of: admin, analyst, viewer",
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = UserORM(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_active=new_user.is_active,
        role=new_user.role,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a user (admin only)."""
    # Get existing user
    stmt = select(UserORM).where(UserORM.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check username uniqueness if updating
    if user_data.username and user_data.username != user.username:
        stmt = select(UserORM).where(UserORM.username == user_data.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    
    # Check email uniqueness if updating
    if user_data.email and user_data.email != user.email:
        stmt = select(UserORM).where(UserORM.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
    
    # Validate role if updating
    if user_data.role and user_data.role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be one of: admin, analyst, viewer",
        )
    
    # Update fields
    update_data = {}
    if user_data.username is not None:
        update_data["username"] = user_data.username
    if user_data.email is not None:
        update_data["email"] = user_data.email
    if user_data.password is not None:
        update_data["hashed_password"] = get_password_hash(user_data.password)
    if user_data.is_active is not None:
        update_data["is_active"] = user_data.is_active
    if user_data.role is not None:
        update_data["role"] = user_data.role
    
    if update_data:
        stmt = update(UserORM).where(UserORM.id == user_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()
        # Refresh user to get updated values
        await db.refresh(user)
        # Re-query to ensure we have latest data
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role=user.role,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[UserORM, Depends(require_admin)] = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (admin only)."""
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    # Get user
    stmt = select(UserORM).where(UserORM.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Delete user
    stmt = delete(UserORM).where(UserORM.id == user_id)
    await db.execute(stmt)
    await db.commit()
    
    return None

