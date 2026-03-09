"""
Users CRUD
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.database import get_db
from api.models import User, Order
from api.schemas import UserCreate, UserUpdate, UserResponse, BatchUserItem, BatchUserResponse
from api.services import users


class ErrorResponse(BaseModel):
    detail: str


router = APIRouter()


# ---------- LIST USERS ----------

@router.get(
    "",
    response_model=list[UserResponse],
    summary="List users",
    description="Returns a paginated list of users with optional filtering and sorting.",
)
def list_users(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(User).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET USER ----------

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user",
    description="Retrieve a single user by ID.",
    responses={404: {"description": "User not found", "model": ErrorResponse}},
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# ---------- CREATE USER ----------

@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Create user",
    description="Creates a new user.",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email already exists", "model": ErrorResponse},
    },
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    user = User(**payload.model_dump())

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists",
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create user: {str(exc)}",
        )


# ---------- UPDATE USER ----------

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Partially update user fields.",
    responses={
        404: {"description": "User not found", "model": ErrorResponse},
        409: {"description": "Email conflict", "model": ErrorResponse},
    },
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflict with existing data (email may already exist)",
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update user: {str(exc)}",
        )


# ---------- DELETE USER ----------

@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete user",
    description="Deletes a user if they do not have related orders.",
    responses={
        404: {"description": "User not found", "model": ErrorResponse},
        409: {"description": "User has related orders", "model": ErrorResponse},
    },
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    orders_count = db.scalar(
        select(func.count()).where(Order.user_id == user_id)
    )

    if orders_count and orders_count > 0:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete user with existing orders",
        )

    try:
        db.delete(user)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete user: {str(exc)}",
        )


# ---------- BATCH LOAD ----------

@router.post(
    "/batch",
    response_model=BatchUserResponse,
)
def batch_users(
    users_list: List[BatchUserItem],
    db: Session = Depends(get_db),
):
    return users.batch_import_users(
        db,
        [u.dict() for u in users_list],
    )