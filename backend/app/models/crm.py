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

class SalesTerritory(AuditBase):
    __tablename__ = "sales_territories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. North, South
    assigned_salesperson_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    # Relationships
    customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="territory")

class Customer(AuditBase):
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_type: Mapped[str] = mapped_column(String(50), default="COMPANY") # COMPANY, INDIVIDUAL
    gst_number: Mapped[Optional[str]] = mapped_column(String(50))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    segment: Mapped[str] = mapped_column(String(50), default="SME") # ENTERPRISE, SME, VIP, DISTRIBUTOR, GOVERNMENT
    credit_limit: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    payment_terms: Mapped[str] = mapped_column(String(50), default="NET30")
    territory_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("sales_territories.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Relationships
    territory: Mapped[Optional["SalesTerritory"]] = relationship("SalesTerritory", back_populates="customers")
    contacts: Mapped[List["CustomerContact"]] = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
    addresses: Mapped[List["CustomerAddress"]] = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    notes: Mapped[List["CustomerNote"]] = relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan")
    activity_logs: Mapped[List["CustomerActivityLog"]] = relationship("CustomerActivityLog", back_populates="customer", cascade="all, delete-orphan")
    opportunities: Mapped[List["Opportunity"]] = relationship("Opportunity", back_populates="customer")
    quotations: Mapped[List["Quotation"]] = relationship("Quotation", back_populates="customer")
    sales_orders: Mapped[List["SalesOrder"]] = relationship("SalesOrder", back_populates="customer")
    documents: Mapped[List["CustomerDocument"]] = relationship("CustomerDocument", back_populates="customer", cascade="all, delete-orphan")

class CustomerContact(AuditBase):
    __tablename__ = "customer_contacts"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="contacts")

class CustomerAddress(AuditBase):
    __tablename__ = "customer_addresses"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    address_type: Mapped[str] = mapped_column(String(50), default="BILLING") # BILLING, SHIPPING
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="addresses")

class CustomerNote(AuditBase):
    __tablename__ = "customer_notes"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="notes")

class CustomerActivityLog(AuditBase):
    __tablename__ = "customer_activity_logs"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False) # CALL, EMAIL, MEETING, OPPORTUNITY_CHANGED
    description: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="activity_logs")

class Lead(AuditBase):
    __tablename__ = "leads"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50), default="MANUAL") # WEBSITE, REFERRAL, CAMPAIGN, MANUAL
    status: Mapped[str] = mapped_column(String(50), default="NEW") # NEW, CONTACTED, QUALIFIED, UNQUALIFIED, CONVERTED
    score: Mapped[float] = mapped_column(Float, default=0.0)
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    converted_customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"))

    # Relationships
    activities: Mapped[List["LeadActivity"]] = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")

class LeadActivity(AuditBase):
    __tablename__ = "lead_activities"

    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False) # CALL, EMAIL, MEETING, NOTE
    details: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")

class Opportunity(AuditBase):
    __tablename__ = "opportunities"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), default="PROSPECTING") # PROSPECTING, QUALIFICATION, PROPOSAL, NEGOTIATION, WON, LOST
    probability: Mapped[float] = mapped_column(Float, default=10.0) # percentage
    expected_revenue: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    close_date: Mapped[date] = mapped_column(Date, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(30), default="LOW") # LOW, MEDIUM, HIGH
    competitors: Mapped[Optional[str]] = mapped_column(String(255))
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    lost_reason: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="opportunities")
    products: Mapped[List["OpportunityProduct"]] = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan")
    quotations: Mapped[List["Quotation"]] = relationship("Quotation", back_populates="opportunity")

class OpportunityProduct(AuditBase):
    __tablename__ = "opportunity_products"

    opportunity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    is_upsell: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="products")

class PricingRule(AuditBase):
    __tablename__ = "pricing_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(50), nullable=False) # VIP, ENTERPRISE, SME, etc.
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

class Quotation(AuditBase):
    __tablename__ = "quotations"

    quotation_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="SET NULL"))
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, SUBMITTED, APPROVED, REJECTED, ACCEPTED, CONVERTED
    version: Mapped[int] = mapped_column(Integer, default=1)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="quotations")
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity", back_populates="quotations")
    items: Mapped[List["QuotationItem"]] = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    sales_orders: Mapped[List["SalesOrder"]] = relationship("SalesOrder", back_populates="quotation")

class QuotationItem(AuditBase):
    __tablename__ = "quotation_items"

    quotation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Relationships
    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="items")

class SalesOrder(AuditBase):
    __tablename__ = "sales_orders"

    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    quotation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("quotations.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, PENDING_APPROVAL, APPROVED, SHIPPED, COMPLETED, CANCELLED
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    salesperson_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    shipping_status: Mapped[str] = mapped_column(String(30), default="PENDING") # PENDING, SHIPPED, DELIVERED

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="sales_orders")
    quotation: Mapped[Optional["Quotation"]] = relationship("Quotation", back_populates="sales_orders")
    items: Mapped[List["SalesOrderItem"]] = relationship("SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")

class SalesOrderItem(AuditBase):
    __tablename__ = "sales_order_items"

    sales_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="items")

class CustomerDocument(AuditBase):
    __tablename__ = "customer_documents"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="documents")

class CommunicationTemplate(AuditBase):
    __tablename__ = "communication_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_template: Mapped[str] = mapped_column(String(512), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), default="EMAIL") # EMAIL, SMS

class CRMTask(AuditBase):
    __tablename__ = "crm_tasks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    priority: Mapped[str] = mapped_column(String(30), default="LOW") # LOW, MEDIUM, HIGH
    status: Mapped[str] = mapped_column(String(30), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"))
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))

class CRMMeeting(AuditBase):
    __tablename__ = "crm_meetings"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"))
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))

class CRMCommunication(AuditBase):
    __tablename__ = "crm_communications"

    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"))
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))
    communication_type: Mapped[str] = mapped_column(String(50), nullable=False) # EMAIL, CALL
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    logged_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
