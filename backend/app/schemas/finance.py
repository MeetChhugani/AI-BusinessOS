from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class GeneralLedgerAccountBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    account_type: str # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    parent_id: Optional[UUID] = None
    opening_balance: float = 0.0
    status: str = "ACTIVE"

class GeneralLedgerAccountCreate(GeneralLedgerAccountBase):
    pass

class GeneralLedgerAccountResponse(GeneralLedgerAccountBase):
    id: UUID
    current_balance: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class JournalEntryLineCreate(BaseModel):
    account_id: UUID
    debit: float = 0.0
    credit: float = 0.0
    cost_center_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    region: Optional[str] = None

class JournalEntryLineResponse(BaseModel):
    id: UUID
    account_id: UUID
    debit: float
    credit: float
    cost_center_id: Optional[UUID]
    department_id: Optional[UUID]
    project_id: Optional[UUID]
    region: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str = Field(..., max_length=512)
    source_document: Optional[str] = None
    lines: List[JournalEntryLineCreate]

class JournalEntryResponse(BaseModel):
    id: UUID
    entry_number: str
    entry_date: date
    description: str
    status: str
    source_document: Optional[str]
    lines: List[JournalEntryLineResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InvoiceItemCreate(BaseModel):
    product_id: UUID
    quantity: float
    unit_price: float

class InvoiceItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: float
    unit_price: float
    total_cost: float
    model_config = ConfigDict(from_attributes=True)

class CustomerInvoiceCreate(BaseModel):
    customer_id: UUID
    sales_order_id: Optional[UUID] = None
    payment_terms: str = "NET30"
    items: List[InvoiceItemCreate]

class CustomerInvoiceResponse(BaseModel):
    id: UUID
    invoice_number: str
    customer_id: UUID
    sales_order_id: Optional[UUID]
    issue_date: date
    due_date: date
    payment_terms: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    outstanding_balance: float
    status: str
    created_at: datetime
    items: List[InvoiceItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class VendorBillItemCreate(BaseModel):
    product_id: UUID
    quantity: float
    unit_price: float

class VendorBillItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: float
    unit_price: float
    total_cost: float
    model_config = ConfigDict(from_attributes=True)

class VendorBillCreate(BaseModel):
    supplier_id: UUID
    purchase_order_id: Optional[UUID] = None
    due_date: date
    items: List[VendorBillItemCreate]

class VendorBillResponse(BaseModel):
    id: UUID
    bill_number: str
    supplier_id: UUID
    purchase_order_id: Optional[UUID]
    bill_date: date
    due_date: date
    subtotal: float
    tax_amount: float
    total_amount: float
    outstanding_balance: float
    status: str
    created_at: datetime
    items: List[VendorBillItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class PaymentAllocationCreate(BaseModel):
    invoice_id: Optional[UUID] = None
    vendor_bill_id: Optional[UUID] = None
    allocated_amount: float

class PaymentAllocationResponse(BaseModel):
    id: UUID
    invoice_id: Optional[UUID]
    vendor_bill_id: Optional[UUID]
    allocated_amount: float
    model_config = ConfigDict(from_attributes=True)

class PaymentCreate(BaseModel):
    payment_type: str # CUSTOMER_INFLOW, VENDOR_OUTFLOW, REFUND
    payment_date: date
    amount: float
    payment_method: str = "CASH"
    reference_number: Optional[str] = None
    allocations: List[PaymentAllocationCreate]

class PaymentResponse(BaseModel):
    id: UUID
    payment_number: str
    payment_type: str
    payment_date: date
    amount: float
    payment_method: str
    reference_number: Optional[str]
    status: str
    created_at: datetime
    allocations: List[PaymentAllocationResponse] = []
    model_config = ConfigDict(from_attributes=True)

class AssetCreate(BaseModel):
    name: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    purchase_date: date
    purchase_value: float
    residual_value: float = 0.0
    useful_life_months: int
    asset_account_id: UUID
    depreciation_account_id: UUID

class AssetResponse(BaseModel):
    id: UUID
    asset_number: str
    name: str
    category: str
    purchase_date: date
    purchase_value: float
    residual_value: float
    useful_life_months: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BudgetLineCreate(BaseModel):
    account_id: UUID
    allocated_amount: float

class BudgetLineResponse(BaseModel):
    id: UUID
    account_id: UUID
    allocated_amount: float
    actual_amount: float
    model_config = ConfigDict(from_attributes=True)

class BudgetCreate(BaseModel):
    name: str = Field(..., max_length=100)
    cost_center_id: UUID
    start_date: date
    end_date: date
    lines: List[BudgetLineCreate]

class BudgetResponse(BaseModel):
    id: UUID
    name: str
    cost_center_id: UUID
    start_date: date
    end_date: date
    status: str
    lines: List[BudgetLineResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExpenseClaimCreate(BaseModel):
    expense_category_id: UUID
    amount: float
    claim_date: date
    description: str = Field(..., max_length=512)
    receipt_image_url: Optional[str] = None

class ExpenseClaimResponse(BaseModel):
    id: UUID
    claim_number: str
    employee_id: UUID
    expense_category_id: UUID
    amount: float
    claim_date: date
    description: str
    receipt_image_url: Optional[str]
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
