import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditBase

class Currency(AuditBase):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False) # USD, INR
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    is_base: Mapped[bool] = mapped_column(Boolean, default=False)

class ExchangeRate(AuditBase):
    __tablename__ = "exchange_rates"

    from_currency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("currencies.id", ondelete="CASCADE"), nullable=False)
    to_currency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("currencies.id", ondelete="CASCADE"), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(15, 6), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)

class FiscalYear(AuditBase):
    __tablename__ = "fiscal_years"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN") # OPEN, CLOSED

    periods: Mapped[List["FiscalPeriod"]] = relationship("FiscalPeriod", back_populates="fiscal_year", cascade="all, delete-orphan")

class FiscalPeriod(AuditBase):
    __tablename__ = "fiscal_periods"

    fiscal_year_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_years.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN") # OPEN, CLOSED, LOCKED

    fiscal_year: Mapped["FiscalYear"] = relationship("FiscalYear", back_populates="periods")

class CostCenter(AuditBase):
    __tablename__ = "cost_centers"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

class GeneralLedgerAccount(AuditBase):
    __tablename__ = "general_ledger_accounts"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False) # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="SET NULL"))
    opening_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    current_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    children: Mapped[List["GeneralLedgerAccount"]] = relationship("GeneralLedgerAccount", back_populates="parent", remote_side="GeneralLedgerAccount.id")
    parent: Mapped[Optional["GeneralLedgerAccount"]] = relationship("GeneralLedgerAccount", back_populates="children", remote_side="GeneralLedgerAccount.parent_id")

class ChartOfAccounts(AuditBase):
    __tablename__ = "chart_of_accounts"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

class JournalEntry(AuditBase):
    __tablename__ = "journal_entries"

    entry_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # JE-2026-000001
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT") # DRAFT, POSTED, VOIDED
    source_document: Mapped[Optional[str]] = mapped_column(String(100)) # e.g. INV-2026-001245
    posted_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    lines: Mapped[List["JournalEntryLine"]] = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")

class JournalEntryLine(AuditBase):
    __tablename__ = "journal_entry_lines"

    journal_entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="RESTRICT"), nullable=False)
    debit: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    credit: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    
    # Financial Dimensions
    cost_center_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("cost_centers.id", ondelete="SET NULL"))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"))
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True)) # external ID reference
    region: Mapped[Optional[str]] = mapped_column(String(100))

    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["GeneralLedgerAccount"] = relationship("GeneralLedgerAccount")

class RecurringJournalTemplate(AuditBase):
    __tablename__ = "recurring_journal_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), nullable=False) # MONTHLY, QUARTERLY, ANNUALLY
    next_run_date: Mapped[date] = mapped_column(Date, nullable=False)
    template_data: Mapped[dict] = mapped_column(JSONB, nullable=False) # stores debit/credit lines skeleton

class TaxConfiguration(AuditBase):
    __tablename__ = "tax_configurations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # GST, VAT
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

class TaxRate(AuditBase):
    __tablename__ = "tax_rates"

    tax_configuration_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tax_configurations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False) # percentage e.g. 18.00

class CustomerInvoice(AuditBase):
    __tablename__ = "customer_invoices"

    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # INV-2026-000001
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    sales_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="SET NULL"))
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(50), default="NET30") # NET15, NET30, EOM, IMMEDIATE
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    outstanding_balance: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, PENDING_APPROVAL, APPROVED, ISSUED, PARTIALLY_PAID, PAID, CANCELLED

    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(AuditBase):
    __tablename__ = "invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customer_invoices.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tax_rates.id"))
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    invoice: Mapped["CustomerInvoice"] = relationship("CustomerInvoice", back_populates="items")

class VendorBill(AuditBase):
    __tablename__ = "vendor_bills"

    bill_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # BILL-2026-000001
    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    purchase_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="SET NULL"))
    bill_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    outstanding_balance: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, APPROVED, PARTIALLY_PAID, PAID, CANCELLED

    items: Mapped[List["VendorBillItem"]] = relationship("VendorBillItem", back_populates="vendor_bill", cascade="all, delete-orphan")

class VendorBillItem(AuditBase):
    __tablename__ = "vendor_bill_items"

    vendor_bill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendor_bills.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    vendor_bill: Mapped["VendorBill"] = relationship("VendorBill", back_populates="items")

class Payment(AuditBase):
    __tablename__ = "payments"

    payment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    payment_type: Mapped[str] = mapped_column(String(50), nullable=False) # CUSTOMER_INFLOW, VENDOR_OUTFLOW, REFUND
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="CASH") # CASH, BANK_TRANSFER, CHEQUE
    reference_number: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="POSTED") # POSTED, VOIDED

    allocations: Mapped[List["PaymentAllocation"]] = relationship("PaymentAllocation", back_populates="payment", cascade="all, delete-orphan")

class PaymentAllocation(AuditBase):
    __tablename__ = "payment_allocations"

    payment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customer_invoices.id", ondelete="CASCADE"))
    vendor_bill_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("vendor_bills.id", ondelete="CASCADE"))
    allocated_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")

class Receipt(AuditBase):
    __tablename__ = "receipts"

    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    payment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)

class ExpenseCategory(AuditBase):
    __tablename__ = "expense_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g. TRAVEL, MEALS
    default_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="SET NULL"))

class ExpenseClaim(AuditBase):
    __tablename__ = "expense_claims"

    claim_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    expense_category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_categories.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    claim_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    receipt_image_url: Mapped[Optional[str]] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, SUBMITTED, APPROVED, REIMBURSED, REJECTED

class Asset(AuditBase):
    __tablename__ = "assets"

    asset_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. MACHINERY, VEHICLES
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    purchase_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    residual_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    useful_life_months: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="RESTRICT"), nullable=False)
    depreciation_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE") # ACTIVE, DISPOSED, FULLY_DEPRECIATED

    depreciations: Mapped[List["AssetDepreciation"]] = relationship("AssetDepreciation", back_populates="asset", cascade="all, delete-orphan")

class AssetDepreciation(AuditBase):
    __tablename__ = "asset_depreciations"

    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    depreciation_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    accumulated_depreciation: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    journal_entry_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    asset: Mapped["Asset"] = relationship("Asset", back_populates="depreciations")

class Budget(AuditBase):
    __tablename__ = "budgets"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cost_center_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cost_centers.id", ondelete="CASCADE"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    lines: Mapped[List["BudgetLine"]] = relationship("BudgetLine", back_populates="budget", cascade="all, delete-orphan")

class BudgetLine(AuditBase):
    __tablename__ = "budget_lines"

    budget_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="RESTRICT"), nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    actual_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)

    budget: Mapped["Budget"] = relationship("Budget", back_populates="lines")

class BankAccount(AuditBase):
    __tablename__ = "bank_accounts"

    account_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), default="SAVINGS") # SAVINGS, CURRENT
    gl_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("general_ledger_accounts.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

class BankTransaction(AuditBase):
    __tablename__ = "bank_transactions"

    bank_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    debit: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0) # inflow
    credit: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0) # outflow
    reference_number: Mapped[Optional[str]] = mapped_column(String(100))
    reconciliation_status: Mapped[str] = mapped_column(String(30), default="UNMATCHED") # MATCHED, PARTIALLY_MATCHED, UNMATCHED, IGNORED

class Reconciliation(AuditBase):
    __tablename__ = "reconciliations"

    bank_transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bank_transactions.id", ondelete="CASCADE"), nullable=False)
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    reconciled_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    reconciled_date: Mapped[date] = mapped_column(Date, nullable=False)

class FinancialActivityLog(AuditBase):
    __tablename__ = "financial_activity_logs"

    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. EDIT, POST_JOURNAL
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(512))
    request_id: Mapped[Optional[str]] = mapped_column(String(100))
