"""
Payments CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Payment
from api.schemas import PaymentCreate, PaymentResponse, PaymentUpdate


router = APIRouter()


# ---------- LIST PAYMENTS ----------

@router.get(
    "",
    response_model=list[PaymentResponse],
    summary="List payments",
    description="Returns a paginated list of payments with optional sorting.",
)
def list_payments(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Payment).offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET PAYMENT ----------

@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment",
    description="Retrieve a single payment by ID.",
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = db.get(Payment, payment_id)

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment


# ---------- CREATE PAYMENT ----------

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=201,
    summary="Create payment",
    description="Create a new payment record.",
)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
):
    payment = Payment(**payload.model_dump())

    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

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
            detail=f"Failed to create payment: {str(exc)}",
        )


# ---------- UPDATE PAYMENT ----------

@router.patch(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Update payment",
    description="Partial update of payment fields.",
)
def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    db: Session = Depends(get_db),
):
    payment = db.get(Payment, payment_id)

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(payment, field, value)

    try:
        db.commit()
        db.refresh(payment)
        return payment

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
            detail=f"Failed to update payment: {str(exc)}",
        )


# ---------- DELETE PAYMENT ----------

@router.delete(
    "/{payment_id}",
    status_code=204,
    summary="Delete payment",
    description="Delete a payment record.",
)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = db.get(Payment, payment_id)

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    try:
        db.delete(payment)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete payment: {str(exc)}",
        )