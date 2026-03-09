"""
Business Services
"""

from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------- FUNCTIONS ----------

def get_order_total(db: Session, order_id: int):
    result = db.execute(
        text("SELECT fn_get_order_total(:order_id)"),
        {"order_id": order_id}
    ).scalar()

    return {
        "order_id": order_id,
        "total": result,
    }


def find_free_servers(db: Session, server_type_id: int, start, end):
    result = db.execute(
        text("""
            SELECT * FROM fn_find_free_servers(
                :server_type_id,
                :start_time,
                :end_time
            )
        """),
        {
            "server_type_id": server_type_id,
            "start_time": start,
            "end_time": end,
        }
    ).fetchall()

    return result


# ---------- VIEWS ----------

def get_customer_overview(db: Session):
    return db.execute(
        text("SELECT * FROM v_customer_overview")
    ).fetchall()


def get_active_rentals(db: Session):
    return db.execute(
        text("SELECT * FROM v_active_rentals")
    ).fetchall()


def get_fleet_capacity(db: Session):
    return db.execute(
        text("SELECT * FROM v_fleet_capacity")
    ).fetchall()


def get_server_profitability(db: Session):
    return db.execute(
        text("SELECT * FROM v_server_profitability")
    ).fetchall()


# ---------- TRANSACTIONS ----------

def rent_server(db: Session, user_id: int, server_id: int, start_time: datetime, end_time: datetime):
    with db.begin():
        server_status = db.execute(
            text("SELECT status FROM Servers WHERE server_id = :id FOR UPDATE"),
            {"id": server_id}
        ).scalar()

        if server_status != "available":
            raise Exception("Server not available")

        order_id = db.execute(
            text("""
                INSERT INTO Orders (user_id, server_id, start_time, end_time, status)
                VALUES (:user_id, :server_id, :start, :end, 'pending')
                RETURNING order_id
            """),
            {
                "user_id": user_id,
                "server_id": server_id,
                "start": start_time,
                "end": end_time,
            }
        ).scalar()

        total_price = db.execute(
            text("SELECT fn_get_order_total(:order_id)"),
            {"order_id": order_id}
        ).scalar()

        db.execute(
            text("""
                INSERT INTO Payments (order_id, amount, payment_date, method, status)
                VALUES (:order_id, :amount, NOW(), 'card', 'pending')
            """),
            {
                "order_id": order_id,
                "amount": total_price,
            }
        )

        return {
            "order_id": order_id,
            "total_price": total_price,
        }


def confirm_payment(db: Session, order_id: int, success: bool):
    with db.begin():
        payment_id = db.execute(
            text("""
                SELECT payment_id
                FROM Payments
                WHERE order_id = :order_id
                FOR UPDATE
            """),
            {"order_id": order_id}
        ).scalar()

        if not payment_id:
            raise Exception("Payment not found")

        if success:
            db.execute(
                text("""
                    UPDATE Payments
                    SET status = 'completed'
                    WHERE order_id = :order_id
                """),
                {"order_id": order_id}
            )
            db.execute(
                text("""
                    UPDATE Orders
                    SET status = 'active'
                    WHERE order_id = :order_id
                """),
                {"order_id": order_id}
            )
        else:
            db.execute(
                text("""
                    UPDATE Payments
                    SET status = 'failed'
                    WHERE order_id = :order_id
                """),
                {"order_id": order_id}
            )
            db.execute(
                text("""
                    UPDATE Orders
                    SET status = 'cancelled'
                    WHERE order_id = :order_id
                """),
                {"order_id": order_id}
            )

        return {"status": "updated"}