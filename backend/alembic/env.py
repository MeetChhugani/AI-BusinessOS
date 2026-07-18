import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Ensure backend directory is in python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings
from app.models.base import Base
from app.models.user import User
from app.models.hcm import (
    Department,
    Designation,
    Employee,
    EmployeeSkill,
    SalaryHistory,
    Attendance,
    AttendanceSession,
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    PerformanceReview,
    EmployeeDocument,
    EmployeeNote,
    EmployeeTimeline,
)
from app.models.inventory import (
    Warehouse,
    WarehouseLocation,
    Supplier,
    ProductCategory,
    Unit,
    Product,
    ProductImage,
    ProductVariant,
    ProductSerial,
    ProductBatch,
    Inventory,
    InventoryTransaction,
    StockReservation,
    ReorderRule,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceipt,
    StockTransfer,
    StockTransferItem,
    StockAdjustment,
    ApprovalWorkflow,
    ProductTimeline,
    InventoryAudit,
    InventoryAuditItem,
    InventoryActivityLog,
)
from app.models.crm import (
    SalesTerritory,
    Customer,
    CustomerContact,
    CustomerAddress,
    CustomerNote,
    CustomerActivityLog,
    Lead,
    LeadActivity,
    Opportunity,
    OpportunityProduct,
    PricingRule,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
    CustomerDocument,
    CommunicationTemplate,
    CRMTask,
    CRMMeeting,
    CRMCommunication,
)
from app.models.finance import (
    Currency,
    ExchangeRate,
    FiscalYear,
    FiscalPeriod,
    CostCenter,
    GeneralLedgerAccount,
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    RecurringJournalTemplate,
    TaxConfiguration,
    TaxRate,
    CustomerInvoice,
    InvoiceItem,
    VendorBill,
    VendorBillItem,
    Payment,
    PaymentAllocation,
    Receipt,
    ExpenseCategory,
    ExpenseClaim,
    Asset,
    AssetDepreciation,
    Budget,
    BudgetLine,
    BankAccount,
    BankTransaction,
    Reconciliation,
    FinancialActivityLog,
)

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async connection."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
