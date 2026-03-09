"""
Resources Usage CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import ResourcesUsage
from api.schemas import ResourcesUsageCreate, ResourcesUsageResponse


router = APIRouter()


# ---------- LIST RESOURCES USAGE ----------

@router.get(
    "",
    response_model=list[ResourcesUsageResponse],
    summary="List resource usage entries",
    description="Return a paginated list of server resource usage entries.",
)
def list_resources_usage(
    skip: int = 0,
    limit: int = Query(100, le=500),
    server_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(ResourcesUsage)

    if server_id is not None:
        stmt = stmt.where(ResourcesUsage.server_id == server_id)

    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt)
    return result.scalars().all()


# ---------- GET RESOURCE USAGE ----------

@router.get(
    "/{usage_id}",
    response_model=ResourcesUsageResponse,
    summary="Get resource usage entry",
    description="Retrieve a single resource usage entry by ID.",
)
def get_resource_usage(
    usage_id: int,
    db: Session = Depends(get_db),
):
    usage = db.get(ResourcesUsage, usage_id)

    if not usage:
        raise HTTPException(
            status_code=404,
            detail="Resource usage entry not found",
        )

    return usage


# ---------- CREATE RESOURCE USAGE ----------

@router.post(
    "",
    response_model=ResourcesUsageResponse,
    status_code=201,
    summary="Create resource usage entry",
    description="Add a new resource usage entry for a server.",
)
def create_resource_usage(
    payload: ResourcesUsageCreate,
    db: Session = Depends(get_db),
):
    usage = ResourcesUsage(**payload.model_dump())

    try:
        db.add(usage)
        db.commit()
        db.refresh(usage)
        return usage

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
            detail=f"Failed to create resource usage: {str(exc)}",
        )


# ---------- DELETE RESOURCE USAGE ----------

@router.delete(
    "/{usage_id}",
    status_code=204,
    summary="Delete resource usage entry",
    description="Delete a resource usage entry by ID.",
)
def delete_resource_usage(
    usage_id: int,
    db: Session = Depends(get_db),
):
    usage = db.get(ResourcesUsage, usage_id)

    if not usage:
        raise HTTPException(
            status_code=404,
            detail="Resource usage entry not found",
        )

    try:
        db.delete(usage)
        db.commit()
        return None

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete resource usage: {str(exc)}",
        )