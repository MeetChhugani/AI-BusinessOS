import uuid
from typing import List, Optional, Tuple
from sqlalchemy import and_, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.inventory import (
    Warehouse,
    WarehouseLocation,
    Supplier,
    ProductCategory,
    Unit,
    Product,
    ProductVariant,
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
)
from app.models.user import User

class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

class WarehouseRepository(BaseRepository):
    async def get_all(self, status: Optional[str] = None) -> List[Warehouse]:
        query = select(Warehouse).where(Warehouse.deleted_at.is_(None))
        if status:
            query = query.where(Warehouse.status == status)
        result = await self.db.execute(query.order_by(Warehouse.name))
        return list(result.scalars().all())

    async def get_by_id(self, id: uuid.UUID) -> Optional[Warehouse]:
        query = select(Warehouse).where(and_(Warehouse.id == id, Warehouse.deleted_at.is_(None)))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, warehouse: Warehouse) -> Warehouse:
        self.db.add(warehouse)
        await self.db.commit()
        await self.db.refresh(warehouse)
        return warehouse

    async def update(self, warehouse: Warehouse) -> Warehouse:
        self.db.add(warehouse)
        await self.db.commit()
        await self.db.refresh(warehouse)
        return warehouse

class SupplierRepository(BaseRepository):
    async def get_all(self, status: Optional[str] = None) -> List[Supplier]:
        query = select(Supplier).where(Supplier.deleted_at.is_(None))
        if status:
            query = query.where(Supplier.status == status)
        result = await self.db.execute(query.order_by(Supplier.name))
        return list(result.scalars().all())

    async def get_by_id(self, id: uuid.UUID) -> Optional[Supplier]:
        query = select(Supplier).where(and_(Supplier.id == id, Supplier.deleted_at.is_(None)))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, supplier: Supplier) -> Supplier:
        self.db.add(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)
        return supplier

    async def update(self, supplier: Supplier) -> Supplier:
        self.db.add(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)
        return supplier

class ProductRepository(BaseRepository):
    async def get_all_paginated(
        self,
        search: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        brand: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Product], int]:
        query = select(Product).where(Product.deleted_at.is_(None)).options(
            selectinload(Product.category),
            selectinload(Product.images)
        )
        if search:
            query = query.where(Product.name.icontains(search) | Product.sku.icontains(search) | Product.brand.icontains(search))
        if category_id:
            query = query.where(Product.category_id == category_id)
        if brand:
            query = query.where(Product.brand == brand)
        if status:
            query = query.where(Product.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one() or 0

        # Paginated results
        result = await self.db.execute(query.order_by(Product.name).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_id(self, id: uuid.UUID) -> Optional[Product]:
        query = select(Product).where(and_(Product.id == id, Product.deleted_at.is_(None))).options(
            selectinload(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants),
            selectinload(Product.timelines)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

class InventoryRepository(BaseRepository):
    async def get_or_create_inventory(
        self,
        warehouse_id: uuid.UUID,
        product_id: uuid.UUID,
        variant_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None,
    ) -> Inventory:
        query = select(Inventory).where(
            and_(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
                Inventory.variant_id == variant_id,
                Inventory.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        record = result.scalars().first()
        
        if not record:
            record = Inventory(
                warehouse_id=warehouse_id,
                location_id=location_id,
                product_id=product_id,
                variant_id=variant_id,
                quantity_on_hand=0.0,
                quantity_reserved=0.0,
                quantity_available=0.0,
                quantity_incoming=0.0
            )
            self.db.add(record)
            await self.db.flush()
            
        return record

    async def reserve_stock(
        self,
        warehouse_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: float,
        reference_type: str,
        reference_id: uuid.UUID,
        variant_id: Optional[uuid.UUID] = None,
    ) -> bool:
        inv = await self.get_or_create_inventory(warehouse_id, product_id, variant_id)
        if inv.quantity_available < quantity:
            return False
            
        inv.quantity_reserved += quantity
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        
        reservation = StockReservation(
            inventory_id=inv.id,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            status="ACTIVE"
        )
        self.db.add(reservation)
        await self.db.commit()
        return True

    async def commit_reservation(self, reservation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        query = select(StockReservation).where(and_(StockReservation.id == reservation_id, StockReservation.status == "ACTIVE"))
        res = await self.db.execute(query)
        reservation = res.scalars().first()
        if not reservation:
            return False
            
        # Deduct physical stock
        inv_query = select(Inventory).where(Inventory.id == reservation.inventory_id)
        inv_res = await self.db.execute(inv_query)
        inv = inv_res.scalars().first()
        if not inv:
            return False
            
        inv.quantity_on_hand -= reservation.quantity
        inv.quantity_reserved -= reservation.quantity
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        
        reservation.status = "COMPLETED"
        
        # Log Transaction
        txn = InventoryTransaction(
            inventory_id=inv.id,
            transaction_type="OUTBOUND",
            quantity=-reservation.quantity,
            reference_document=f"RES-{str(reservation_id)[:8]}",
            cost_price=inv.product.cost_price if inv.product else 0.0,
            user_id=user_id,
            notes="Committed reservation dispatch"
        )
        self.db.add(txn)
        await self.db.commit()
        return True

    async def log_stock_movement(
        self,
        warehouse_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: float,
        transaction_type: str, # INBOUND, OUTBOUND, TRANSFER, ADJUSTMENT
        user_id: uuid.UUID,
        variant_id: Optional[uuid.UUID] = None,
        reference_document: Optional[str] = None,
        cost_price: float = 0.0,
        notes: Optional[str] = None
    ) -> Inventory:
        inv = await self.get_or_create_inventory(warehouse_id, product_id, variant_id)
        
        inv.quantity_on_hand += quantity
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        
        txn = InventoryTransaction(
            inventory_id=inv.id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_document=reference_document,
            cost_price=cost_price,
            user_id=user_id,
            notes=notes
        )
        self.db.add(txn)
        await self.db.commit()
        await self.db.refresh(inv)
        return inv

    async def get_valuation(self, warehouse_id: Optional[uuid.UUID] = None) -> float:
        query = select(func.sum(Inventory.quantity_on_hand * Product.cost_price)).join(Product, Product.id == Inventory.product_id)
        if warehouse_id:
            query = query.where(Inventory.warehouse_id == warehouse_id)
        res = await self.db.execute(query)
        return float(res.scalar() or 0.0)

    async def get_low_stock_alerts(self) -> List[dict]:
        query = select(Inventory, ReorderRule).join(
            ReorderRule,
            and_(
                ReorderRule.warehouse_id == Inventory.warehouse_id,
                ReorderRule.product_id == Inventory.product_id
            )
        ).where(Inventory.quantity_available <= ReorderRule.min_stock).options(
            selectinload(Inventory.product),
            selectinload(Inventory.warehouse)
        )
        res = await self.db.execute(query)
        alerts = []
        for inv, rule in res.all():
            alerts.append({
                "warehouse": inv.warehouse.name,
                "product": inv.product.name,
                "sku": inv.product.sku,
                "available": inv.quantity_available,
                "reorder_level": rule.min_stock,
                "reorder_qty": rule.reorder_quantity
            })
        return alerts

class PurchaseOrderRepository(BaseRepository):
    async def get_all_paginated(
        self,
        status: Optional[str] = None,
        supplier_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PurchaseOrder], int]:
        query = select(PurchaseOrder).where(PurchaseOrder.deleted_at.is_(None)).options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.items)
        )
        if status:
            query = query.where(PurchaseOrder.status == status)
        if supplier_id:
            query = query.where(PurchaseOrder.supplier_id == supplier_id)
            
        count_q = select(func.count()).select_from(query.subquery())
        c_res = await self.db.execute(count_q)
        total = c_res.scalar_one() or 0
        
        result = await self.db.execute(query.order_by(desc(PurchaseOrder.created_at)).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_id(self, id: uuid.UUID) -> Optional[PurchaseOrder]:
        query = select(PurchaseOrder).where(and_(PurchaseOrder.id == id, PurchaseOrder.deleted_at.is_(None))).options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.items)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, order: PurchaseOrder) -> PurchaseOrder:
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
