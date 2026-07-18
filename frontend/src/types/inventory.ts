export interface Warehouse {
  id: string;
  name: string;
  code: string;
  address?: string;
  capacity: number;
  status: 'ACTIVE' | 'INACTIVE';
  manager_id?: string;
  created_at: string;
}

export interface WarehouseLocation {
  id: string;
  warehouse_id: string;
  zone: string;
  rack?: string;
  shelf?: string;
  bin?: string;
  code: string;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface Supplier {
  id: string;
  name: string;
  code: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  gst_number?: string;
  address?: string;
  payment_terms: string;
  rating: number;
  late_delivery_count: number;
  defect_rate: number;
  cancellation_rate: number;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
}

export interface ProductCategory {
  id: string;
  name: string;
  code: string;
  description?: string;
  parent_id?: string;
  icon?: string;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface Unit {
  id: string;
  name: string;
  code: string;
}

export interface ProductImage {
  id: string;
  product_id: string;
  image_url: string;
  is_primary: boolean;
  thumbnail_url?: string;
}

export interface Product {
  id: string;
  sku: string;
  barcode?: string;
  qr_code?: string;
  name: string;
  description?: string;
  category_id?: string;
  brand?: string;
  cost_price: number;
  selling_price: number;
  tax_rate: number;
  weight?: number;
  dimensions?: string;
  unit_id?: string;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
  images?: ProductImage[];
  category?: ProductCategory;
}

export interface ProductVariant {
  id: string;
  product_id: string;
  sku: string;
  barcode?: string;
  name: string;
  cost_price?: number;
  selling_price?: number;
  attribute_values?: Record<string, string>;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface Inventory {
  id: string;
  warehouse_id: string;
  location_id?: string;
  product_id: string;
  variant_id?: string;
  quantity_on_hand: number;
  quantity_reserved: number;
  quantity_available: number;
  quantity_incoming: number;
}

export interface InventoryTransaction {
  id: string;
  inventory_id: string;
  transaction_type: 'INBOUND' | 'OUTBOUND' | 'TRANSFER' | 'ADJUSTMENT' | 'RETURN' | 'DAMAGE' | 'EXPIRY';
  quantity: number;
  reference_document?: string;
  cost_price: number;
  user_id: string;
  notes?: string;
  created_at: string;
}

export interface PurchaseOrderItem {
  id: string;
  purchase_order_id: string;
  product_id: string;
  variant_id?: string;
  quantity_ordered: number;
  quantity_received: number;
  unit_price: number;
  tax_rate: number;
  total_cost: number;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier_id: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'RECEIVED' | 'CANCELLED';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_status: 'PENDING' | 'PAID';
  created_by_id: string;
  created_at: string;
  supplier?: Supplier;
  items?: PurchaseOrderItem[];
}

export interface StockTransferItem {
  id: string;
  stock_transfer_id: string;
  product_id: string;
  variant_id?: string;
  quantity: number;
}

export interface StockTransfer {
  id: string;
  transfer_number: string;
  source_warehouse_id: string;
  destination_warehouse_id: string;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'IN_TRANSIT' | 'COMPLETED' | 'CANCELLED';
  requested_by_id: string;
  approved_by_id?: string;
  created_at: string;
  items?: StockTransferItem[];
}

export interface StockAdjustment {
  id: string;
  adjustment_number: string;
  warehouse_id: string;
  inventory_id: string;
  original_quantity: number;
  new_quantity: number;
  variance: number;
  reason: string;
  adjusted_by_id: string;
  created_at: string;
}

export interface ApprovalWorkflow {
  id: string;
  entity_type: 'PURCHASE_ORDER' | 'STOCK_TRANSFER' | 'LEAVE_REQUEST';
  entity_id: string;
  approver_id: string;
  sequence_order: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  comments?: string;
  reviewed_at?: string;
}

export interface ProductTimeline {
  id: string;
  product_id: string;
  event_type: 'CREATED' | 'PRICE_CHANGED' | 'SUPPLIER_CHANGED' | 'STOCK_UPDATED' | 'TRANSFERRED';
  event_date: string;
  description: string;
}

export interface InventoryAudit {
  id: string;
  audit_number: string;
  warehouse_id: string;
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED';
  started_at?: string;
  completed_at?: string;
  audited_by_id: string;
  items?: InventoryAuditItem[];
}

export interface InventoryAuditItem {
  id: string;
  inventory_audit_id: string;
  inventory_id: string;
  system_quantity: number;
  physical_quantity: number;
  variance: number;
  status: 'MATCHED' | 'DISCREPANCY' | 'CORRECTED';
}
