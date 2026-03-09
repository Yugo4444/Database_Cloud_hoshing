"""
Server Logs CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import ServerLog
from api.schemas import ServerLogCreate, ServerLogResponse


router = APIRouter()


# ---------- LIST SERVER LOGS ----------

@router.get(
    "",
    response_model=list[ServerLogResponse],
    summary="List server logs",
    description="Return a paginated list of server logs with optional filtering.",
)
def list_server_logs(
    skip: int = 0,
    limit: int = Query(100, le=500),
    server_id: int | None = None,
    event_type: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(ServerLog)

    if server_id is not None:
        stmt = stmt.where(ServerLog.server_id == server_id)

    if event_type is not None:
        stmt = stmt.where(ServerLog.event_type == event_type)

    if severity is not None:
        stmt = stmt.where(ServerLog.severity == severity)

    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET SERVER LOG ----------

@router.get(
    "/{log_id}",
    response_model=ServerLogResponse,
    summary="Get server log",
    description="Retrieve a single server log by ID.",
)
def get_server_log(
    log_id: int,
    db: Session = Depends(get_db),
):
    log = db.get(ServerLog, log_id)

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Server log not found",
        )

    return log


# ---------- CREATE SERVER LOG ----------

@router.post(
    "",
    response_model=ServerLogResponse,
    status_code=201,
    summary="Create server log",
    description="Create a new server log entry.",
)
def create_server_log(
    payload: ServerLogCreate,
    db: Session = Depends(get_db),
):
    log = ServerLog(**payload.model_dump())

    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

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
            detail=f"Failed to create server log: {str(exc)}",
        )


# ---------- DELETE SERVER LOG ----------

@router.delete(
    "/{log_id}",
    status_code=204,
    summary="Delete server log",
    description="Delete a server log entry by ID.",
)
def delete_server_log(
    log_id: int,
    db: Session = Depends(get_db),
):
    log = db.get(ServerLog, log_id)

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Server log not found",
        )

    try:
        db.delete(log)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete server log: {str(exc)}",
        )