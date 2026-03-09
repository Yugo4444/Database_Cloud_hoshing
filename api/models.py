from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    text,
    JSON
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


# ---------- USERS ----------
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    tickets: Mapped[List["SupportTicket"]] = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("role IN ('customer', 'admin', 'operator', 'support')", name="users_role_check"),
    )


# ---------- SERVER TYPES ----------
class ServerType(Base):
    __tablename__ = "servertypes"

    server_type_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    price_per_hour: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default="0.0")
    support_level: Mapped[str] = mapped_column(String(20), nullable=False, server_default="basic")

    servers: Mapped[List["Server"]] = relationship("Server", back_populates="server_type")

    __table_args__ = (
        CheckConstraint("discount >= 0 AND discount <= 1", name="servertype_discount_check"),
    )


# ---------- SERVERS ----------
class Server(Base):
    __tablename__ = "servers"

    server_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    server_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("servertypes.server_type_id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    server_type: Mapped["ServerType"] = relationship("ServerType", back_populates="servers")
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True, unique=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="server", cascade="all, delete-orphan")
    resources_usage: Mapped[List["ResourcesUsage"]] = relationship("ResourcesUsage", back_populates="server", cascade="all, delete-orphan")
    maintenance: Mapped[List["ServerMaintenance"]] = relationship("ServerMaintenance", back_populates="server", cascade="all, delete-orphan")
    logs: Mapped[List["ServerLog"]] = relationship("ServerLog", back_populates="server", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="servertagassignments",
        back_populates="servers",
        overlaps="tag_assignments"
    )

    tag_assignments: Mapped[List["ServerTagAssignment"]] = relationship(
        "ServerTagAssignment",
        back_populates="server",
        cascade="all, delete-orphan",
        overlaps="tags"
    )
    __table_args__ = (
        CheckConstraint("status IN ('available', 'rented', 'maintenance', 'offline')", name="servers_status_check"),
    )


# ---------- ORDERS ----------
class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("servers.server_id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    server: Mapped["Server"] = relationship("Server", back_populates="orders")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('pending','active','completed','cancelled')", name="orders_status_check"),
    )


# ---------- TAGS ----------
class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    servers: Mapped[List["Server"]] = relationship(
        "Server",
        secondary="servertagassignments",
        back_populates="tags",
        overlaps="server_assignments,tag_assignments,server"
    )

    server_assignments: Mapped[List["ServerTagAssignment"]] = relationship(
        "ServerTagAssignment",
        back_populates="tag",
        cascade="all, delete-orphan",
        overlaps="tags,servers,server"
    )

# ---------- SERVER TAG ASSIGNMENTS ----------
class ServerTagAssignment(Base):
    __tablename__ = "servertagassignments"

    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("servers.server_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.tag_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)

    server: Mapped["Server"] = relationship(
        "Server",
        back_populates="tag_assignments",
        overlaps="tags,servers,server_assignments"
    )

    tag: Mapped["Tag"] = relationship(
        "Tag",
        back_populates="server_assignments",
        overlaps="tags,servers,tag_assignments"
    )

# ---------- PAYMENTS ----------
class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    order: Mapped["Order"] = relationship("Order", back_populates="payments")

    __table_args__ = (
        CheckConstraint("method IN ('card','bank_transfer','paypal','crypto')", name="payments_method_check"),
        CheckConstraint("status IN ('pending','completed','failed','refunded')", name="payments_status_check"),
    )


# ---------- RESOURCES USAGE ----------
class ResourcesUsage(Base):
    __tablename__ = "resourcesusage"

    usage_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("servers.server_id", ondelete="CASCADE"))
    cpu_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    ram_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    storage_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    server: Mapped["Server"] = relationship("Server", back_populates="resources_usage")


# ---------- SERVER MAINTENANCE ----------
class ServerMaintenance(Base):
    __tablename__ = "servermaintenance"

    maintenance_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("servers.server_id", ondelete="CASCADE"))
    performed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=True)
    maintenance_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    server: Mapped["Server"] = relationship("Server", back_populates="maintenance")
    performed_by_user: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        CheckConstraint("status IN ('scheduled','in_progress','completed','cancelled')", name="maintenance_status_check"),
    )


# ---------- SERVER LOGS ----------
class ServerLog(Base):
    __tablename__ = "serverlogs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(Integer, ForeignKey("servers.server_id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    performed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    server: Mapped["Server"] = relationship("Server", back_populates="logs")

    __table_args__ = (
        CheckConstraint("event_type IN ('reboot','error','update','shutdown','startup')", name="server_logs_event_type_check"),
        CheckConstraint("severity IN ('info','warning','critical')", name="server_logs_severity_check"),
    )


# ---------- SUPPORT TICKETS ----------
class SupportTicket(Base):
    __tablename__ = "supporttickets"

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="tickets")

    __table_args__ = (
        CheckConstraint("status IN ('open','in_progress','resolved','closed')", name="support_ticket_status_check"),
        CheckConstraint("priority IN ('low','medium','high','critical')", name="support_ticket_priority_check"),
    )