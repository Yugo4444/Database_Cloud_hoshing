"""
FastAPI backend for Cloud / Hosting Server Rental System.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import engine
from api.routes import (
    users,
    servers,
    orders,
    payments,
    server_logs,
    maintenance,
    resources_usage,
    support_tickets,
    business,
    tags,
    servertagassignment,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Cloud Hosting Server Rental API",
    description=(
        "REST API for server rental"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- CRUD ROUTERS ----------

app.include_router(users.router, prefix="/api/users", tags=["Users CRUD"])
app.include_router(servers.router, prefix="/api/servers", tags=["Servers CRUD"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders CRUD"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments CRUD"])
app.include_router(server_logs.router, prefix="/api/server_logs", tags=["Server Logs CRUD"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["Maintenance CRUD"])
app.include_router(resources_usage.router, prefix="/api/resources_usage", tags=["Resource Usage CRUD"])
app.include_router(support_tickets.router, prefix="/api/support_tickets", tags=["Support Tickets CRUD"])
app.include_router(tags.router, prefix="/api/tags", tags=["Tags CRUD"])
app.include_router(servertagassignment.router, prefix="/api/server_tag_asignment", tags=["Server-Tag Assignment CRUD"])

# ---------- BUSINESS OPERATIONS ----------

app.include_router(business.router, prefix="/api", tags=["Business Operations"])

# ---------- HEALTH CHECK ----------

@app.get("/health")
def health():
    return {"status": "ok"}