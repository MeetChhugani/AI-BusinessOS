from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.employees import router as employees_router
from app.api.v1.departments import router as departments_router
from app.api.v1.designations import router as designations_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.leaves import router as leaves_router
from app.api.v1.performance import router as performance_router
from app.api.v1.documents import router as documents_router
from app.api.v1.organization import router as organization_router
from app.api.v1.warehouses import router as warehouses_router
from app.api.v1.products import router as products_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.purchase_orders import router as purchase_orders_router
from app.api.v1.transfers import router as transfers_router
from app.api.v1.audits import router as audits_router
from app.api.v1.customers import router as customers_router
from app.api.v1.leads import router as leads_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.quotations import router as quotations_router
from app.api.v1.orders import router as orders_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.accounts import router as accounts_router
from app.api.v1.journal import router as journal_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.vendor_bills import router as vendor_bills_router
from app.api.v1.payments import router as payments_router
from app.api.v1.bank import router as bank_router
from app.api.v1.assets import router as assets_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.reports import router as reports_router
from app.config.settings import settings
from app.exceptions.handlers import register_exception_handlers
from app.logging.config import setup_logging
from app.middleware.rate_limit import GlobalRateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.services.redis_service import redis_service

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    redis_service.connect()
    yield
    # Shutdown events
    await redis_service.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AI BusinessOS - Enterprise SaaS ERP core foundation. "
        "Provides foundational Authentication, Role-Based Access Control, "
        "Auditing, Caching, and Tracing modules."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "System", "description": "System monitoring and health checks"},
        {"name": "Authentication", "description": "User registration, JWT session issuance, and MFA/recovery hooks"},
    ],
)

# 1. Tracing Middleware (Injects request id)
app.add_middleware(RequestIDMiddleware)

# 2. Strict Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Global Rate Limiter (100 req/min)
app.add_middleware(GlobalRateLimitMiddleware)

# Register Custom Global Exception Handlers
register_exception_handlers(app)

# Include v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(employees_router, prefix=settings.API_V1_STR)
app.include_router(departments_router, prefix=settings.API_V1_STR)
app.include_router(designations_router, prefix=settings.API_V1_STR)
app.include_router(attendance_router, prefix=settings.API_V1_STR)
app.include_router(leaves_router, prefix=settings.API_V1_STR)
app.include_router(performance_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(organization_router, prefix=settings.API_V1_STR)
app.include_router(warehouses_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(suppliers_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(purchase_orders_router, prefix=settings.API_V1_STR)
app.include_router(transfers_router, prefix=settings.API_V1_STR)
app.include_router(audits_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(leads_router, prefix=settings.API_V1_STR)
app.include_router(opportunities_router, prefix=settings.API_V1_STR)
app.include_router(quotations_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(accounts_router, prefix=settings.API_V1_STR)
app.include_router(journal_router, prefix=settings.API_V1_STR)
app.include_router(invoices_router, prefix=settings.API_V1_STR)
app.include_router(vendor_bills_router, prefix=settings.API_V1_STR)
app.include_router(payments_router, prefix=settings.API_V1_STR)
app.include_router(bank_router, prefix=settings.API_V1_STR)
app.include_router(assets_router, prefix=settings.API_V1_STR)
app.include_router(budgets_router, prefix=settings.API_V1_STR)
app.include_router(expenses_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["System"])
def read_root() -> dict:
    return {
        "message": "Welcome to AI BusinessOS ERP Platform Foundation",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
