"""
Server Maintenance CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import ServerMaintenance
from api.schemas import (
    ServerMaintenanceCreate,
    ServerMaintenanceResponse,
    ServerMaintenanceUpdate,
)


router = APIRouter()


# ---------- LIST MAINTENANCE ENTRIES ----------

@router.get(
    "",
    response_model=list[ServerMaintenanceResponse],
    summary="List server maintenance entries",
    description="Return a paginated list of server maintenance events.",
)
def list_maintenance(
    skip: int = 0,
    limit: int = Query(100, le=500),
    server_id: int | None = None,
    performed_by: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(ServerMaintenance)

    if server_id is not None:
        stmt = stmt.where(ServerMaintenance.server_id == server_id)

    if performed_by is not None:
        stmt = stmt.where(ServerMaintenance.performed_by == performed_by)

    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET MAINTENANCE ENTRY ----------

@router.get(
    "/{maintenance_id}",
    response_model=ServerMaintenanceResponse,
    summary="Get maintenance entry",
    description="Retrieve a single server maintenance entry by ID.",
)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
):
    maintenance = db.get(ServerMaintenance, maintenance_id)

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Server maintenance entry not found",
        )

    return maintenance


# ---------- CREATE MAINTENANCE ENTRY ----------

@router.post(
    "",
    response_model=ServerMaintenanceResponse,
    status_code=201,
    summary="Create maintenance entry",
    description="Schedule a new server maintenance event.",
)
def create_maintenance(
    payload: ServerMaintenanceCreate,
    db: Session = Depends(get_db),
):
    maintenance = ServerMaintenance(**payload.model_dump())

    try:
        db.add(maintenance)
        db.commit()
        db.refresh(maintenance)
        return maintenance

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
            detail=f"Failed to create maintenance entry: {str(exc)}",
        )


# ---------- UPDATE MAINTENANCE ENTRY ----------

@router.patch(
    "/{maintenance_id}",
    response_model=ServerMaintenanceResponse,
    summary="Update maintenance entry",
    description="Partial update of a server maintenance entry.",
)
def update_maintenance(
    maintenance_id: int,
    payload: ServerMaintenanceUpdate,
    db: Session = Depends(get_db),
):
    maintenance = db.get(ServerMaintenance, maintenance_id)

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Server maintenance entry not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(maintenance, field, value)

    try:
        db.commit()
        db.refresh(maintenance)
        return maintenance

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
            detail=f"Failed to update maintenance entry: {str(exc)}",
        )


# ---------- DELETE MAINTENANCE ENTRY ----------

@router.delete(
    "/{maintenance_id}",
    status_code=204,
    summary="Delete maintenance entry",
    description="Delete a server maintenance entry by ID.",
)
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
):
    maintenance = db.get(ServerMaintenance, maintenance_id)

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Server maintenance entry not found",
        )

    try:
        db.delete(maintenance)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete maintenance entry: {str(exc)}",
        )