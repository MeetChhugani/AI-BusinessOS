from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class WarehouseBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)
    address: Optional[str] = Field(None, max_length=512)
    capacity: float = 0.0
    status: str = "ACTIVE"
    manager_id: Optional[UUID] = None

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseResponse(WarehouseBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SupplierBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)
    contact_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    gst_number: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=512)
    payment_terms: str = "NET30"
    rating: float = 5.0
    status: str = "ACTIVE"

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: UUID
    late_delivery_count: int
    defect_rate: float
    cancellation_rate: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductCategoryBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=512)
    parent_id: Optional[UUID] = None
    icon: Optional[str] = Field(None, max_length=50)
    status: str = "ACTIVE"

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryResponse(ProductCategoryBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductImageBase(BaseModel):
    image_url: str
    is_primary: bool = False
    thumbnail_url: Optional[str] = None

class ProductImageCreate(ProductImageBase):
    pass

class ProductImageResponse(ProductImageBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    sku: str = Field(..., max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    qr_code: Optional[str] = Field(None, max_length=255)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = Field(None, max_length=100)
    cost_price: float
    selling_price: float
    tax_rate: float = 0.0
    weight: Optional[float] = None
    dimensions: Optional[str] = Field(None, max_length=100)
    unit_id: Optional[UUID] = None
    status: str = "ACTIVE"

class ProductCreate(ProductBase):
    images: Optional[List[ProductImageCreate]] = None

class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    images: List[ProductImageResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ProductVariantBase(BaseModel):
    sku: str = Field(..., max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    name: str = Field(..., max_length=255)
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    attribute_values: Optional[dict] = None
    status: str = "ACTIVE"

class ProductVariantCreate(ProductVariantBase):
    product_id: UUID

class ProductVariantResponse(ProductVariantBase):
    id: UUID
    product_id: UUID
    model_config = ConfigDict(from_attributes=True)

class InventoryResponse(BaseModel):
    id: UUID
    warehouse_id: UUID
    location_id: Optional[UUID] = None
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity_on_hand: float
    quantity_reserved: float
    quantity_available: float
    quantity_incoming: float
    model_config = ConfigDict(from_attributes=True)

class InventoryTransactionResponse(BaseModel):
    id: UUID
    inventory_id: UUID
    transaction_type: str
    quantity: float
    reference_document: Optional[str]
    cost_price: float
    user_id: UUID
    notes: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity_ordered: float
    unit_price: float
    tax_rate: float = 0.0

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: UUID
    quantity_received: float
    total_cost: float
    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderCreate(BaseModel):
    supplier_id: UUID
    items: List[PurchaseOrderItemCreate]
    tax_amount: float = 0.0
    discount_amount: float = 0.0

class PurchaseOrderResponse(BaseModel):
    id: UUID
    po_number: str
    supplier_id: UUID
    status: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_status: str
    created_by_id: UUID
    created_at: datetime
    items: List[PurchaseOrderItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class StockTransferItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: float

class StockTransferItemCreate(StockTransferItemBase):
    pass

class StockTransferItemResponse(StockTransferItemBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class StockTransferCreate(BaseModel):
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    items: List[StockTransferItemCreate]

class StockTransferResponse(BaseModel):
    id: UUID
    transfer_number: str
    source_warehouse_id: UUID
    destination_warehouse_id: UUID
    status: str
    requested_by_id: UUID
    approved_by_id: Optional[UUID] = None
    created_at: datetime
    items: List[StockTransferItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class StockAdjustmentCreate(BaseModel):
    warehouse_id: UUID
    product_id: UUID
    variant_id: Optional[UUID] = None
    new_quantity: float
    reason: str = Field(..., max_length=255)

class StockAdjustmentResponse(BaseModel):
    id: UUID
    adjustment_number: str
    warehouse_id: UUID
    inventory_id: UUID
    original_quantity: float
    new_quantity: float
    variance: float
    reason: str
    adjusted_by_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ApprovalWorkflowAction(BaseModel):
    approved: bool
    comments: Optional[str] = Field(None, max_length=512)

class ApprovalWorkflowResponse(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    approver_id: UUID
    sequence_order: int
    status: str
    comments: Optional[str]
    reviewed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
