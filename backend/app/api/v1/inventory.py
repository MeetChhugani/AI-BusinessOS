from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.inventory import Inventory, InventoryTransaction, StockAdjustment, Product, Warehouse
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryResponse, InventoryTransactionResponse, StockAdjustmentCreate, StockAdjustmentResponse

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryResponse], summary="List inventory stock balances")
async def list_inventory(
    warehouse_id: Optional[UUID] = None,
    product_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[Inventory]:
    query = select(Inventory).where(Inventory.deleted_at.is_(None))
    if warehouse_id:
        query = query.where(Inventory.warehouse_id == warehouse_id)
    if product_id:
        query = query.where(Inventory.product_id == product_id)
        
    result = await db.execute(query)
    return list(result.scalars().all())

@router.get("/valuation", summary="Get inventory valuation sum")
async def get_valuation(
    warehouse_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
):
    repo = InventoryRepository(db)
    val = await repo.get_valuation(warehouse_id)
    return {"warehouse_id": str(warehouse_id) if warehouse_id else "ALL", "valuation": val}

@router.get("/low-stock", summary="List items below reorder points")
async def get_low_stock(
    db: AsyncSession = Depends(get_db_session)
):
    repo = InventoryRepository(db)
    return await repo.get_low_stock_alerts()

@router.post("/adjust", response_model=StockAdjustmentResponse, status_code=201, summary="Log a stock adjustment reconciliation")
async def adjust_stock(
    body: StockAdjustmentCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "WAREHOUSE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> StockAdjustment:
    repo = InventoryRepository(db)
    inv = await repo.get_or_create_inventory(body.warehouse_id, body.product_id, body.variant_id)
    
    original = inv.quantity_on_hand
    variance = body.new_quantity - original
    
    # Update inventory stock level
    inv.quantity_on_hand = body.new_quantity
    inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
    
    # Generate adjustment code
    count_query = select(func.count(StockAdjustment.id))
    r_count = await db.execute(count_query)
    total = r_count.scalar() or 0
    adj_number = f"ADJ-{total + 1:04d}"
    
    # Create adjustment log
    adj = StockAdjustment(
        adjustment_number=adj_number,
        warehouse_id=body.warehouse_id,
        inventory_id=inv.id,
        original_quantity=original,
        new_quantity=body.new_quantity,
        variance=variance,
        reason=body.reason,
        adjusted_by_id=current_user.id
    )
    db.add(adj)
    
    # Create transaction log
    txn = InventoryTransaction(
        inventory_id=inv.id,
        transaction_type="ADJUSTMENT",
        quantity=variance,
        reference_document=adj_number,
        cost_price=inv.product.cost_price if inv.product else 0.0,
        user_id=current_user.id,
        notes=body.reason
    )
    db.add(txn)
    await db.commit()
    await db.refresh(adj)
    
    logger.info("stock_adjustment_recorded", adjustment_number=adj_number, variance=variance)
    return adj

@router.get("/transactions", response_model=List[InventoryTransactionResponse], summary="Retrieve transaction logs")
async def get_transactions(
    inventory_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[InventoryTransaction]:
    query = select(InventoryTransaction)
    if inventory_id:
        query = query.where(InventoryTransaction.inventory_id == inventory_id)
    result = await db.execute(query.order_by(InventoryTransaction.created_at.desc()))
    return list(result.scalars().all())
from sqlalchemy import func
