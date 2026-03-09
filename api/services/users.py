"""
Users Service: Batch import and single user creation
"""

from typing import List
from sqlalchemy import text
from sqlalchemy.orm import Session


# ---------- SINGLE USER CREATION ----------

def create_single_user(db: Session, user: dict):
    with db.begin():
        db.execute(
            text("""
                INSERT INTO Users (
                    first_name,
                    last_name,
                    email,
                    phone,
                    role
                )
                VALUES (
                    :first_name,
                    :last_name,
                    :email,
                    :phone,
                    :role
                )
            """),
            {
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "phone": user.get("phone"),
                "role": user["role"],
            }
        )


# ---------- BATCH USER IMPORT ----------

def batch_import_users(db: Session, users: List[dict]):
    success_count = 0
    errors = []

    for user in users:
        try:
            create_single_user(db, user)
            success_count += 1
        except Exception as exc:
            errors.append(f"{user['email']}: {str(exc)}")

    return {
        "total": len(users),
        "imported": success_count,
        "errors": errors,
    }