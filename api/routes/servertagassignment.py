"""
ServerTagAssignments CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import ServerTagAssignment
from api.schemas import (
    ServerTagAssignmentCreate,
    ServerTagAssignmentResponse,
    ServerTagAssignmentUpdate,
)


router = APIRouter()


# ---------- LIST SERVER TAG ASSIGNMENTS ----------

@router.get(
    "",
    response_model=list[ServerTagAssignmentResponse],
    summary="List server-tag assignments",
)
def list_assignments(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(ServerTagAssignment).offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET ALL ASSIGNMENTS FOR SERVER ----------

@router.get(
    "/{server_id}",
    response_model=list[ServerTagAssignmentResponse],
    summary="Get all tags assigned to a server",
    description="Retrieve all server-tag assignments for a given server_id.",
)
def get_assignments_for_server(
    server_id: int,
    db: Session = Depends(get_db),
):
    stmt = select(ServerTagAssignment).where(ServerTagAssignment.server_id == server_id)
    result = db.execute(stmt)
    assignments = result.scalars().all()

    if not assignments:
        raise HTTPException(
            status_code=404,
            detail="No assignments found for this server",
        )

    return assignments


# ---------- CREATE ASSIGNMENT ----------

@router.post(
    "",
    response_model=ServerTagAssignmentResponse,
    status_code=201,
    summary="Create server-tag assignment",
)
def create_assignment(
    payload: ServerTagAssignmentCreate,
    db: Session = Depends(get_db),
):
    assignment = ServerTagAssignment(**payload.model_dump())

    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

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
            detail=f"Failed to create assignment: {str(exc)}",
        )


# ---------- DELETE ASSIGNMENT ----------

@router.delete(
    "/{server_id}/{tag_id}",
    status_code=204,
    summary="Delete server-tag assignment",
)
def delete_assignment(
    server_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
):
    assignment = db.get(ServerTagAssignment, {"server_id": server_id, "tag_id": tag_id})

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    try:
        db.delete(assignment)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete assignment: {str(exc)}",
        )