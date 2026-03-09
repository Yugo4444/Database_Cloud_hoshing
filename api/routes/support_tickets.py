"""
Support Tickets CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import SupportTicket
from api.schemas import SupportTicketCreate, SupportTicketResponse, SupportTicketUpdate


router = APIRouter()


# ---------- LIST SUPPORT TICKETS ----------

@router.get(
    "",
    response_model=list[SupportTicketResponse],
    summary="List support tickets",
    description="Returns a paginated list of support tickets with optional filtering.",
)
def list_support_tickets(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(SupportTicket).offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET SUPPORT TICKET ----------

@router.get(
    "/{ticket_id}",
    response_model=SupportTicketResponse,
    summary="Get support ticket",
    description="Retrieve a single support ticket by ID.",
)
def get_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.get(SupportTicket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    return ticket


# ---------- CREATE SUPPORT TICKET ----------

@router.post(
    "",
    response_model=SupportTicketResponse,
    status_code=201,
    summary="Create support ticket",
    description="Create a new support ticket.",
)
def create_support_ticket(
    payload: SupportTicketCreate,
    db: Session = Depends(get_db),
):
    ticket = SupportTicket(**payload.model_dump())

    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

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
            detail=f"Failed to create support ticket: {str(exc)}",
        )


# ---------- UPDATE SUPPORT TICKET ----------

@router.patch(
    "/{ticket_id}",
    response_model=SupportTicketResponse,
    summary="Update support ticket",
    description="Partial update of support ticket fields.",
)
def update_support_ticket(
    ticket_id: int,
    payload: SupportTicketUpdate,
    db: Session = Depends(get_db),
):
    ticket = db.get(SupportTicket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ticket, field, value)

    try:
        db.commit()
        db.refresh(ticket)
        return ticket

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
            detail=f"Failed to update support ticket: {str(exc)}",
        )


# ---------- DELETE SUPPORT TICKET ----------

@router.delete(
    "/{ticket_id}",
    status_code=204,
    summary="Delete support ticket",
    description="Delete a support ticket.",
)
def delete_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.get(SupportTicket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    try:
        db.delete(ticket)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete support ticket: {str(exc)}",
        )