"""
Servers CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Server
from api.schemas import ServerCreate, ServerResponse, ServerUpdate


router = APIRouter()


# ---------- LIST SERVERS ----------

@router.get(
    "",
    response_model=list[ServerResponse],
    summary="List servers",
    description="Returns a paginated list of servers with optional filtering and sorting.",
)
def list_servers(
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Server).offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET SERVER ----------

@router.get(
    "/{server_id}",
    response_model=ServerResponse,
    summary="Get server",
    description="Retrieve a single server by ID.",
)
def get_server(
    server_id: int,
    db: Session = Depends(get_db),
):
    server = db.get(Server, server_id)

    if not server:
        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )

    return server


# ---------- CREATE SERVER ----------

@router.post(
    "",
    response_model=ServerResponse,
    status_code=201,
    summary="Create server",
    description="Create a new server.",
)
def create_server(
    payload: ServerCreate,
    db: Session = Depends(get_db),
):
    server = Server(**payload.model_dump())

    try:
        db.add(server)
        db.commit()
        db.refresh(server)
        return server

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
            detail=f"Failed to create server: {str(exc)}",
        )


# ---------- UPDATE SERVER ----------

@router.patch(
    "/{server_id}",
    response_model=ServerResponse,
    summary="Update server",
    description="Partial update of server fields.",
)
def update_server(
    server_id: int,
    payload: ServerUpdate,
    db: Session = Depends(get_db),
):
    server = db.get(Server, server_id)

    if not server:
        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(server, field, value)

    try:
        db.commit()
        db.refresh(server)
        return server

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
            detail=f"Failed to update server: {str(exc)}",
        )


# ---------- DELETE SERVER ----------

@router.delete(
    "/{server_id}",
    status_code=204,
    summary="Delete server",
    description="Delete a server.",
)
def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
):
    server = db.get(Server, server_id)

    if not server:
        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )

    try:
        db.delete(server)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete server: {str(exc)}",
        )