"""
Orders CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Order
from api.schemas import OrderCreate, OrderResponse, OrderUpdate


router = APIRouter()


# ---------- LIST ORDERS ----------

@router.get(
    "",
    response_model=list[OrderResponse],
    summary="List orders",
    description="Returns a paginated list of orders with optional sorting.",
)
def list_orders(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Order).offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET ORDER ----------

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order",
    description="Retrieve a single order by ID.",
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order


# ---------- CREATE ORDER ----------

@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
    summary="Create order",
    description="Create a new rental order.",
)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=400,
            detail="end_time must be after start_time",
        )

    order = Order(**payload.model_dump())

    try:
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Conflict: {exc.orig}",
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create order: {str(exc)}",
        )


# ---------- UPDATE ORDER ----------

@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order",
    description="Partial update of order fields.",
)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "start_time" in update_data or "end_time" in update_data:
        start_time = update_data.get("start_time", order.start_time)
        end_time = update_data.get("end_time", order.end_time)

        if end_time <= start_time:
            raise HTTPException(
                status_code=400,
                detail="end_time must be after start_time",
            )

    for field, value in update_data.items():
        setattr(order, field, value)

    try:
        db.commit()
        db.refresh(order)
        return order

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Conflict: {exc.orig}",
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order: {str(exc)}",
        )


# ---------- DELETE ORDER ----------

@router.delete(
    "/{order_id}",
    status_code=204,
    summary="Delete order",
    description="Delete an order record.",
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    try:
        db.delete(order)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete order: {str(exc)}",
        )