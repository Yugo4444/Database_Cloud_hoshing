from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.services import business
from api.schemas import *


router = APIRouter()


# ---------- FUNCTIONS ----------

@router.get("/orders/{order_id}/total", response_model=OrderTotalResponse)
def get_order_total(
    order_id: int,
    db: Session = Depends(get_db),
):
    return business.get_order_total(db, order_id)


@router.get("/free-servers", response_model=List[FreeServerResponse])
def find_free_servers(
    server_type_id: int,
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db),
):
    return business.find_free_servers(
        db,
        server_type_id,
        start_time,
        end_time,
    )


# ---------- VIEWS ----------

@router.get(
    "/customers-overview",
    response_model=List[CustomerOverviewResponse],
)
def customers_overview(
    db: Session = Depends(get_db),
):
    return business.get_customer_overview(db)


@router.get(
    "/active-rentals",
    response_model=List[ActiveRentalResponse],
)
def active_rentals(
    db: Session = Depends(get_db),
):
    return business.get_active_rentals(db)


@router.get(
    "/fleet-capacity",
    response_model=List[FleetCapacityResponse],
)
def fleet_capacity(
    db: Session = Depends(get_db),
):
    return business.get_fleet_capacity(db)


@router.get(
    "/server-profitability",
    response_model=List[ServerProfitabilityResponse],
)
def server_profitability(
    db: Session = Depends(get_db),
):
    return business.get_server_profitability(db)


# ---------- RENT SERVER ----------

@router.post("/rent", response_model=RentServerResponse)
def rent_server(
    request: RentServerRequest,
    db: Session = Depends(get_db),
):
    try:
        return business.rent_server(
            db,
            user_id=request.user_id,
            server_id=request.server_id,
            start_time=request.start_time,
            end_time=request.end_time,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- CONFIRM PAYMENT ----------

@router.post(
    "/confirm-payment",
    response_model=ConfirmPaymentResponse,
)
def confirm_payment(
    request: ConfirmPaymentRequest,
    db: Session = Depends(get_db),
):
    try:
        business.confirm_payment(
            db,
            order_id=request.order_id,
            success=request.success,
        )
        return {"message": "Payment processed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))