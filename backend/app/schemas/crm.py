from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class CustomerContactBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=100)
    is_primary: bool = False

class CustomerContactCreate(CustomerContactBase):
    pass

class CustomerContactResponse(CustomerContactBase):
    id: UUID
    customer_id: UUID
    model_config = ConfigDict(from_attributes=True)

class CustomerBase(BaseModel):
    name: str = Field(..., max_length=255)
    customer_type: str = "COMPANY"
    gst_number: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    segment: str = "SME"
    credit_limit: float = 0.0
    payment_terms: str = "NET30"
    territory_id: Optional[UUID] = None
    status: str = "ACTIVE"

class CustomerCreate(CustomerBase):
    contacts: Optional[List[CustomerContactCreate]] = None

class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    contacts: List[CustomerContactResponse] = []
    model_config = ConfigDict(from_attributes=True)

class LeadBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: str = "MANUAL"
    status: str = "NEW"
    score: float = 0.0
    assigned_to_id: Optional[UUID] = None

class LeadCreate(LeadBase):
    pass

class LeadResponse(LeadBase):
    id: UUID
    converted_customer_id: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OpportunityProductBase(BaseModel):
    product_id: UUID
    quantity: float = 1.0
    unit_price: float

class OpportunityProductCreate(OpportunityProductBase):
    pass

class OpportunityProductResponse(OpportunityProductBase):
    id: UUID
    is_upsell: bool
    model_config = ConfigDict(from_attributes=True)

class OpportunityBase(BaseModel):
    name: str = Field(..., max_length=255)
    customer_id: UUID
    stage: str = "PROSPECTING"
    probability: float = 10.0
    expected_revenue: float
    close_date: date
    risk_level: str = "LOW"
    competitors: Optional[str] = Field(None, max_length=255)
    assigned_to_id: Optional[UUID] = None

class OpportunityCreate(OpportunityBase):
    products: Optional[List[OpportunityProductCreate]] = None

class OpportunityResponse(OpportunityBase):
    id: UUID
    lost_reason: Optional[str] = None
    created_at: datetime
    products: List[OpportunityProductResponse] = []
    model_config = ConfigDict(from_attributes=True)

class QuotationItemCreate(BaseModel):
    product_id: UUID
    quantity: float
    unit_price: float

class QuotationItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: float
    unit_price: float
    tax_rate: float
    total_cost: float
    model_config = ConfigDict(from_attributes=True)

class QuotationCreate(BaseModel):
    customer_id: UUID
    opportunity_id: Optional[UUID] = None
    items: List[QuotationItemCreate]
    valid_until: date
    discount_amount: float = 0.0

class QuotationResponse(BaseModel):
    id: UUID
    quotation_number: str
    customer_id: UUID
    opportunity_id: Optional[UUID] = None
    status: str
    version: int
    valid_until: date
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    created_at: datetime
    items: List[QuotationItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class SalesOrderItemCreate(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: float
    unit_price: float

class SalesOrderCreate(BaseModel):
    customer_id: UUID
    quotation_id: Optional[UUID] = None
    items: List[SalesOrderItemCreate]
    discount_amount: float = 0.0

class SalesOrderResponse(BaseModel):
    id: UUID
    order_number: str
    customer_id: UUID
    quotation_id: Optional[UUID] = None
    status: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    shipping_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CRMTaskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    due_date: datetime
    priority: str = "LOW"
    customer_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None

class CRMTaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    due_date: datetime
    priority: str
    status: str
    assigned_to_id: Optional[UUID]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
