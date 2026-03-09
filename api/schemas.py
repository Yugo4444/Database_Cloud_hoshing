from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- USER ----------
class UserBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    role: str = Field(..., pattern="^(customer|admin|operator|support)$")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    role: Optional[str] = Field(None, pattern="^(customer|admin|operator|support)$")


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    created_at: datetime


# ---------- SERVER ----------
class ServerBase(BaseModel):
    name: str = Field(..., max_length=200)
    server_type_id: int
    ip_address: Optional[str] = None
    status: str = Field(..., pattern="^(available|rented|maintenance|offline)$")


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    server_type_id: Optional[int] = None
    ip_address: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(available|rented|maintenance|offline)$")


class ServerResponse(ServerBase):
    model_config = ConfigDict(from_attributes=True)
    server_id: int
    created_at: datetime


# ---------- ORDER ----------
class OrderBase(BaseModel):
    user_id: int
    server_id: int
    start_time: datetime
    end_time: datetime
    status: str = Field(..., pattern="^(pending|active|completed|cancelled)$")


class OrderCreate(OrderBase):
    status: str = Field("pending", pattern="^(pending|active|completed|cancelled)$")


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|active|completed|cancelled)$")


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    order_id: int


# ---------- PAYMENT ----------
class PaymentBase(BaseModel):
    order_id: int
    amount: Decimal = Field(..., gt=0)
    method: str = Field(..., pattern="^(card|bank_transfer|paypal|crypto)$")
    status: str = Field(..., pattern="^(pending|completed|failed|refunded)$")


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    method: Optional[str] = Field(None, pattern="^(card|bank_transfer|paypal|crypto)$")
    status: Optional[str] = Field(None, pattern="^(pending|completed|failed|refunded)$")


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(from_attributes=True)
    payment_id: int
    payment_date: datetime


# ---------- RESOURCES USAGE ----------
class ResourcesUsageBase(BaseModel):
    server_id: int
    cpu_used: Decimal = Field(..., ge=0, le=100)
    ram_used: Decimal = Field(..., ge=0, le=100)
    storage_used: Decimal = Field(..., ge=0, le=100)


class ResourcesUsageCreate(ResourcesUsageBase):
    pass


class ResourcesUsageResponse(ResourcesUsageBase):
    model_config = ConfigDict(from_attributes=True)
    usage_id: int
    timestamp: datetime


# ---------- SERVER TYPES ----------
class ServerTypeBase(BaseModel):
    type_name: str
    description: Optional[str] = None
    price_per_hour: Decimal
    discount: Decimal = Field(0.0, ge=0, le=1)
    support_level: str = Field("basic", pattern="^(basic|standard|premium)$")


class ServerTypeCreate(ServerTypeBase):
    pass


class ServerTypeUpdate(BaseModel):
    type_name: Optional[str] = None
    description: Optional[str] = None
    price_per_hour: Optional[Decimal] = None
    discount: Optional[Decimal] = Field(None, ge=0, le=1)
    support_level: Optional[str] = Field(None, pattern="^(basic|standard|premium)$")


class ServerTypeResponse(ServerTypeBase):
    model_config = ConfigDict(from_attributes=True)
    server_type_id: int


# ---------- SERVER MAINTENANCE ----------
class ServerMaintenanceBase(BaseModel):
    server_id: int
    maintenance_date: datetime
    description: Optional[str] = None
    status: str = Field(..., pattern="^(scheduled|in_progress|completed|cancelled)$")
    performed_by: Optional[int] = None


class ServerMaintenanceCreate(ServerMaintenanceBase):
    pass


class ServerMaintenanceUpdate(BaseModel):
    maintenance_date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|in_progress|completed|cancelled)$")
    performed_by: Optional[int] = None


class ServerMaintenanceResponse(ServerMaintenanceBase):
    model_config = ConfigDict(from_attributes=True)
    maintenance_id: int


# ---------- SERVER LOGS ----------
class ServerLogBase(BaseModel):
    server_id: int
    event_type: str = Field(..., pattern="^(reboot|error|update|shutdown|startup)$")
    description: Optional[str] = None
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    performed_by: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None


class ServerLogCreate(ServerLogBase):
    pass


class ServerLogResponse(ServerLogBase):
    model_config = ConfigDict(from_attributes=True)
    log_id: int
    logged_at: datetime


# ---------- SUPPORT TICKETS ----------
class SupportTicketBase(BaseModel):
    user_id: int
    subject: str = Field(..., max_length=200)
    description: str
    status: str = Field(..., pattern="^(open|in_progress|resolved|closed)$")
    priority: str = Field(..., pattern="^(low|medium|high|critical)$")


class SupportTicketCreate(SupportTicketBase):
    pass


class SupportTicketUpdate(BaseModel):
    subject: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(open|in_progress|resolved|closed)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")


class SupportTicketResponse(SupportTicketBase):
    model_config = ConfigDict(from_attributes=True)
    ticket_id: int
    created_at: datetime
    updated_at: Optional[datetime]


# ---------- TAGS ----------
class TagBase(BaseModel):
    tag_name: str = Field(..., max_length=100)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    tag_name: Optional[str] = Field(None, max_length=100)


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)
    tag_id: int


# ---------- SERVER TAG ASSIGNMENTS ----------
class ServerTagAssignmentBase(BaseModel):
    server_id: int
    tag_id: int


class ServerTagAssignmentCreate(ServerTagAssignmentBase):
    pass


class ServerTagAssignmentUpdate(BaseModel):
    server_id: Optional[int] = None
    tag_id: Optional[int] = None


class ServerTagAssignmentResponse(ServerTagAssignmentBase):
    model_config = ConfigDict(from_attributes=True)


# ---------- FUNCTION RESPONSES ----------
class OrderTotalResponse(BaseModel):
    order_id: int
    total: Decimal


class FreeServerResponse(BaseModel):
    free_server_id: int
    server_name: str
    ip: Optional[str]
    type_name: str


# ---------- VIEW RESPONSES ----------
class CustomerOverviewResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    total_orders: int
    total_paid: Decimal
    active_tickets: int


class ActiveRentalResponse(BaseModel):
    order_id: int
    customer_email: str
    server_name: str
    ip_address: Optional[str]
    type_name: str
    start_time: datetime
    end_time: datetime
    price_per_hour: Decimal


class FleetCapacityResponse(BaseModel):
    type_name: str
    total_servers: int
    available_now: int
    currently_rented: int
    under_maintenance: int
    occupancy_rate_percent: Decimal


class ServerProfitabilityResponse(BaseModel):
    server_id: int
    server_name: str
    type_name: str
    total_earned: Decimal
    successful_rentals_count: int


# ---------- RENT SERVER ----------
class RentServerRequest(BaseModel):
    user_id: int
    server_id: int
    start_time: datetime
    end_time: datetime


class RentServerResponse(BaseModel):
    order_id: int
    total_price: Decimal


# ---------- CONFIRM PAYMENT ----------
class ConfirmPaymentRequest(BaseModel):
    order_id: int
    success: bool


class ConfirmPaymentResponse(BaseModel):
    message: str


# ---------- BATCH LOAD ----------
class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"
    operator = "operator"
    support = "support"


class BatchUserItem(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole


class BatchUserResponse(BaseModel):
    total: int
    imported: int
    errors: List[str]