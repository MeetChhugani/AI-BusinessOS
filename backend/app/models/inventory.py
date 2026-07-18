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

class Warehouse(AuditBase):
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(512))
    capacity: Mapped[float] = mapped_column(Float, default=0.0)  # cubic meters / weight
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"))

    # Relationships
    locations: Mapped[List["WarehouseLocation"]] = relationship("WarehouseLocation", back_populates="warehouse", cascade="all, delete-orphan")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="warehouse")

class WarehouseLocation(AuditBase):
    __tablename__ = "warehouse_locations"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., Zone A
    rack: Mapped[Optional[str]] = mapped_column(String(50))        # e.g., Rack 3
    shelf: Mapped[Optional[str]] = mapped_column(String(50))       # e.g., Shelf B
    bin: Mapped[Optional[str]] = mapped_column(String(50))         # e.g., Bin 12
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False) # e.g., WH-A-3-B-12
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="locations")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="location")

class Supplier(AuditBase):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    gst_number: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(String(512))
    payment_terms: Mapped[str] = mapped_column(String(50), default="NET30")  # e.g., NET30, NET60
    rating: Mapped[float] = mapped_column(Float, default=5.0)
    
    # Supplier Analytics / Supplier Score metrics
    late_delivery_count: Mapped[int] = mapped_column(Integer, default=0)
    defect_rate: Mapped[float] = mapped_column(Float, default=0.0) # percentage
    cancellation_rate: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Relationships
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier")

class ProductCategory(AuditBase):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="SET NULL"))
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Relationships
    parent: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", remote_side="ProductCategory.id", back_populates="children")
    children: Mapped[List["ProductCategory"]] = relationship("ProductCategory", back_populates="parent")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")

class Unit(AuditBase):
    __tablename__ = "units"

    name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., Kilogram, Litre, Box
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False) # e.g., KG, L, BX

class Product(AuditBase):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    qr_code: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="SET NULL"))
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    cost_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0) # e.g. 18.00 for 18%
    weight: Mapped[Optional[float]] = mapped_column(Float)
    dimensions: Mapped[Optional[str]] = mapped_column(String(100)) # e.g. 10x20x30
    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("units.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Relationships
    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="products")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="product")
    timelines: Mapped[List["ProductTimeline"]] = relationship("ProductTimeline", back_populates="product", cascade="all, delete-orphan")

class ProductImage(AuditBase):
    __tablename__ = "product_images"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1024))

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="images")

class ProductVariant(AuditBase):
    __tablename__ = "product_variants"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False) # e.g., iPhone 15 - Red
    cost_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    selling_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    attribute_values: Mapped[Optional[dict]] = mapped_column(JSONB) # e.g., {"color": "Red"}
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="variant")

class ProductSerial(AuditBase):
    __tablename__ = "product_serials"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"))
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="SET NULL"))
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouse_locations.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), default="AVAILABLE") # AVAILABLE, RESERVED, SOLD, DAMAGED

class ProductBatch(AuditBase):
    __tablename__ = "product_batches"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    batch_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    manufacture_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    initial_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    current_quantity: Mapped[float] = mapped_column(Float, nullable=False)

class Inventory(AuditBase):
    __tablename__ = "inventory"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouse_locations.id", ondelete="SET NULL"))
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"))
    
    # Core Quantity tracking
    quantity_on_hand: Mapped[float] = mapped_column(Float, default=0.0)   # Physical stock
    quantity_reserved: Mapped[float] = mapped_column(Float, default=0.0)  # Allocated for sales/transfers
    quantity_available: Mapped[float] = mapped_column(Float, default=0.0) # on_hand - reserved
    quantity_incoming: Mapped[float] = mapped_column(Float, default=0.0)  # On ordered POs

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="inventory")
    location: Mapped[Optional["WarehouseLocation"]] = relationship("WarehouseLocation", back_populates="inventory")
    product: Mapped["Product"] = relationship("Product", back_populates="inventory")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="inventory")
    transactions: Mapped[List["InventoryTransaction"]] = relationship("InventoryTransaction", back_populates="inventory")

class InventoryTransaction(AuditBase):
    __tablename__ = "inventory_transactions"

    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False) # INBOUND, OUTBOUND, TRANSFER, ADJUSTMENT, RETURN, DAMAGE, EXPIRY
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    reference_document: Mapped[Optional[str]] = mapped_column(String(100)) # PO number, GRN number, Transfer number
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_batches.id", ondelete="SET NULL"))
    cost_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False) # Valuation record
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(512))

    # Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="transactions")

class StockReservation(AuditBase):
    __tablename__ = "stock_reservations"

    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. SALES_ORDER, TRANSFER
    reference_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(25), default="ACTIVE") # ACTIVE, COMPLETED, CANCELLED

class ReorderRule(AuditBase):
    __tablename__ = "reorder_rules"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"))
    min_stock: Mapped[float] = mapped_column(Float, nullable=False)
    max_stock: Mapped[float] = mapped_column(Float, nullable=False)
    safety_stock: Mapped[float] = mapped_column(Float, default=0.0)
    reorder_quantity: Mapped[float] = mapped_column(Float, nullable=False)

class PurchaseOrder(AuditBase):
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, SUBMITTED, APPROVED, RECEIVED, CANCELLED
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="purchase_orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    goods_receipts: Mapped[List["GoodsReceipt"]] = relationship("GoodsReceipt", back_populates="purchase_order")

class PurchaseOrderItem(AuditBase):
    __tablename__ = "purchase_order_items"

    purchase_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"))
    quantity_ordered: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_received: Mapped[float] = mapped_column(Float, default=0.0)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")

class GoodsReceipt(AuditBase):
    __tablename__ = "goods_receipts"

    grn_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    received_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    received_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(512))

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="goods_receipts")

class StockTransfer(AuditBase):
    __tablename__ = "stock_transfers"

    transfer_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    source_warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    destination_warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT") # DRAFT, PENDING_APPROVAL, IN_TRANSIT, COMPLETED, CANCELLED
    requested_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    # Relationships
    items: Mapped[List["StockTransferItem"]] = relationship("StockTransferItem", back_populates="stock_transfer", cascade="all, delete-orphan")

class StockTransferItem(AuditBase):
    __tablename__ = "stock_transfer_items"

    stock_transfer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("stock_transfers.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    stock_transfer: Mapped["StockTransfer"] = relationship("StockTransfer", back_populates="items")

class StockAdjustment(AuditBase):
    __tablename__ = "stock_adjustments"

    adjustment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    original_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    new_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    variance: Mapped[float] = mapped_column(Float, nullable=False) # new_quantity - original_quantity
    reason: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. DAMAGED, CYCLE_COUNT_DISCREPANCY
    adjusted_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

class ApprovalWorkflow(AuditBase):
    __tablename__ = "approval_workflows"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. PURCHASE_ORDER, STOCK_TRANSFER, LEAVE_REQUEST
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    approver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(35), default="PENDING") # PENDING, APPROVED, REJECTED
    comments: Mapped[Optional[str]] = mapped_column(String(512))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

class ProductTimeline(AuditBase):
    __tablename__ = "product_timelines"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # CREATED, PRICE_CHANGED, SUPPLIER_CHANGED, STOCK_UPDATED, TRANSFERRED
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="timelines")

class InventoryAudit(AuditBase):
    __tablename__ = "inventory_audits"

    audit_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED") # SCHEDULED, IN_PROGRESS, COMPLETED
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    audited_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    items: Mapped[List["InventoryAuditItem"]] = relationship("InventoryAuditItem", back_populates="audit", cascade="all, delete-orphan")

class InventoryAuditItem(AuditBase):
    __tablename__ = "inventory_audit_items"

    inventory_audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory_audits.id", ondelete="CASCADE"), nullable=False)
    inventory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    system_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    physical_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    variance: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="MATCHED") # MATCHED, DISCREPANCY, CORRECTED

    # Relationships
    audit: Mapped["InventoryAudit"] = relationship("InventoryAudit", back_populates="items")

class InventoryActivityLog(AuditBase):
    __tablename__ = "inventory_activity_logs"

    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. STOCK_RECEIVED, TRANSFER_APPROVED
    details: Mapped[str] = mapped_column(String(1024), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
