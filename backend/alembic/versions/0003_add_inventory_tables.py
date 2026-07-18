"""add inventory tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-18 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. warehouses
    op.create_table(
        'warehouses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('capacity', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('manager_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouses_code'), 'warehouses', ['code'], unique=True)
    op.create_index(op.f('ix_warehouses_id'), 'warehouses', ['id'], unique=False)

    # 2. warehouse_locations
    op.create_table(
        'warehouse_locations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=False),
        sa.Column('zone', sa.String(length=50), nullable=False),
        sa.Column('rack', sa.String(length=50), nullable=True),
        sa.Column('shelf', sa.String(length=50), nullable=True),
        sa.Column('bin', sa.String(length=50), nullable=True),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_locations_code'), 'warehouse_locations', ['code'], unique=True)
    op.create_index(op.f('ix_warehouse_locations_id'), 'warehouse_locations', ['id'], unique=False)

    # 3. suppliers
    op.create_table(
        'suppliers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('gst_number', sa.String(length=50), nullable=True),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('payment_terms', sa.String(length=50), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('late_delivery_count', sa.Integer(), nullable=False),
        sa.Column('defect_rate', sa.Float(), nullable=False),
        sa.Column('cancellation_rate', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_code'), 'suppliers', ['code'], unique=True)
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)

    # 4. product_categories
    op.create_table(
        'product_categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['product_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_categories_code'), 'product_categories', ['code'], unique=True)
    op.create_index(op.f('ix_product_categories_id'), 'product_categories', ['id'], unique=False)

    # 5. units
    op.create_table(
        'units',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_units_code'), 'units', ['code'], unique=True)

    # 6. products
    op.create_table(
        'products',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('qr_code', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('cost_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('selling_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('dimensions', sa.String(length=100), nullable=True),
        sa.Column('unit_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['product_categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_barcode'), 'products', ['barcode'], unique=False)
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)

    # 7. product_images
    op.create_table(
        'product_images',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('image_url', sa.String(length=1024), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. product_variants
    op.create_table(
        'product_variants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('cost_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('selling_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_variants_barcode'), 'product_variants', ['barcode'], unique=False)
    op.create_index(op.f('ix_product_variants_id'), 'product_variants', ['id'], unique=False)
    op.create_index(op.f('ix_product_variants_sku'), 'product_variants', ['sku'], unique=True)

    # 9. product_serials
    op.create_table(
        'product_serials',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=True),
        sa.Column('location_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['location_id'], ['warehouse_locations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_serials_serial_number'), 'product_serials', ['serial_number'], unique=True)

    # 10. product_batches
    op.create_table(
        'product_batches',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('batch_number', sa.String(length=100), nullable=False),
        sa.Column('manufacture_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('initial_quantity', sa.Float(), nullable=False),
        sa.Column('current_quantity', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_batches_batch_number'), 'product_batches', ['batch_number'], unique=False)

    # 11. inventory
    op.create_table(
        'inventory',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=False),
        sa.Column('location_id', sa.UUID(), nullable=True),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('quantity_on_hand', sa.Float(), nullable=False),
        sa.Column('quantity_reserved', sa.Float(), nullable=False),
        sa.Column('quantity_available', sa.Float(), nullable=False),
        sa.Column('quantity_incoming', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['location_id'], ['warehouse_locations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. inventory_transactions
    op.create_table(
        'inventory_transactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('inventory_id', sa.UUID(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('reference_document', sa.String(length=100), nullable=True),
        sa.Column('batch_id', sa.UUID(), nullable=True),
        sa.Column('cost_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('notes', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['batch_id'], ['product_batches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. stock_reservations
    op.create_table(
        'stock_reservations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('inventory_id', sa.UUID(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('reference_type', sa.String(length=100), nullable=False),
        sa.Column('reference_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=25), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. reorder_rules
    op.create_table(
        'reorder_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('min_stock', sa.Float(), nullable=False),
        sa.Column('max_stock', sa.Float(), nullable=False),
        sa.Column('safety_stock', sa.Float(), nullable=False),
        sa.Column('reorder_quantity', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. purchase_orders
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('po_number', sa.String(length=50), nullable=False),
        sa.Column('supplier_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('payment_status', sa.String(length=30), nullable=False),
        sa.Column('created_by_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_orders_po_number'), 'purchase_orders', ['po_number'], unique=True)

    # 16. purchase_order_items
    op.create_table(
        'purchase_order_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('purchase_order_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('quantity_ordered', sa.Float(), nullable=False),
        sa.Column('quantity_received', sa.Float(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('total_cost', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. goods_receipts
    op.create_table(
        'goods_receipts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('grn_number', sa.String(length=50), nullable=False),
        sa.Column('purchase_order_id', sa.UUID(), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=False),
        sa.Column('received_by_id', sa.UUID(), nullable=False),
        sa.Column('received_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['received_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goods_receipts_grn_number'), 'goods_receipts', ['grn_number'], unique=True)

    # 18. stock_transfers
    op.create_table(
        'stock_transfers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('transfer_number', sa.String(length=50), nullable=False),
        sa.Column('source_warehouse_id', sa.UUID(), nullable=False),
        sa.Column('destination_warehouse_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('requested_by_id', sa.UUID(), nullable=False),
        sa.Column('approved_by_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['source_warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['destination_warehouse_id'], ['warehouses.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_transfers_transfer_number'), 'stock_transfers', ['transfer_number'], unique=True)

    # 19. stock_transfer_items
    op.create_table(
        'stock_transfer_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('stock_transfer_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('variant_id', sa.UUID(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['stock_transfer_id'], ['stock_transfers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 20. stock_adjustments
    op.create_table(
        'stock_adjustments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('adjustment_number', sa.String(length=50), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=False),
        sa.Column('inventory_id', sa.UUID(), nullable=False),
        sa.Column('original_quantity', sa.Float(), nullable=False),
        sa.Column('new_quantity', sa.Float(), nullable=False),
        sa.Column('variance', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('adjusted_by_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['adjusted_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_adjustments_adjustment_number'), 'stock_adjustments', ['adjustment_number'], unique=True)

    # 21. approval_workflows
    op.create_table(
        'approval_workflows',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('approver_id', sa.UUID(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=35), nullable=False),
        sa.Column('comments', sa.String(length=512), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )

    # 22. product_timelines
    op.create_table(
        'product_timelines',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 23. inventory_audits
    op.create_table(
        'inventory_audits',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('audit_number', sa.String(length=50), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('audited_by_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['audited_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_audits_audit_number'), 'inventory_audits', ['audit_number'], unique=True)

    # 24. inventory_audit_items
    op.create_table(
        'inventory_audit_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('inventory_audit_id', sa.UUID(), nullable=False),
        sa.Column('inventory_id', sa.UUID(), nullable=False),
        sa.Column('system_quantity', sa.Float(), nullable=False),
        sa.Column('physical_quantity', sa.Float(), nullable=False),
        sa.Column('variance', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inventory_audit_id'], ['inventory_audits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 25. inventory_activity_logs
    op.create_table(
        'inventory_activity_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('warehouse_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('details', sa.String(length=1024), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('inventory_activity_logs')
    op.drop_table('inventory_audit_items')
    op.drop_table('inventory_audits')
    op.drop_table('product_timelines')
    op.drop_table('approval_workflows')
    op.drop_table('stock_adjustments')
    op.drop_table('stock_transfer_items')
    op.drop_table('stock_transfers')
    op.drop_table('goods_receipts')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('reorder_rules')
    op.drop_table('stock_reservations')
    op.drop_table('inventory_transactions')
    op.drop_table('inventory')
    op.drop_table('product_batches')
    op.drop_table('product_serials')
    op.drop_table('product_variants')
    op.drop_table('product_images')
    op.drop_table('products')
    op.drop_table('units')
    op.drop_table('product_categories')
    op.drop_table('suppliers')
    op.drop_table('warehouse_locations')
    op.drop_table('warehouses')
