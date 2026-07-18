from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.inventory import (
    StockTransfer,
    StockTransferItem,
    Inventory,
    InventoryTransaction,
    ApprovalWorkflow,
)
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import (
    ApprovalWorkflowAction,
    StockTransferCreate,
    StockTransferResponse,
)

router = APIRouter(prefix="/transfers", tags=["Transfers"])

@router.get("", response_model=List[StockTransferResponse], summary="List stock transfers")
async def list_transfers(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[StockTransfer]:
    query = select(StockTransfer).where(StockTransfer.deleted_at.is_(None)).options(
        selectinload(StockTransfer.items)
    )
    if status:
        query = query.where(StockTransfer.status == status)
    result = await db.execute(query.order_by(StockTransfer.created_at.desc()))
    return list(result.scalars().all())

@router.post("", response_model=StockTransferResponse, status_code=201, summary="Create a stock transfer request")
async def create_transfer(
    body: StockTransferCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "WAREHOUSE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> StockTransfer:
    if body.source_warehouse_id == body.destination_warehouse_id:
        raise ValidationException("Source and destination warehouses must be different")

    # Generate transfer number
    count_q = select(func.count(StockTransfer.id))
    r_c = await db.execute(count_q)
    total = r_c.scalar() or 0
    tf_num = f"ST-{total + 1:04d}"

    items_to_add = []
    for it in body.items:
        items_to_add.append(
            StockTransferItem(
                product_id=it.product_id,
                variant_id=it.variant_id,
                quantity=it.quantity
            )
        )

    transfer = StockTransfer(
        transfer_number=tf_num,
        source_warehouse_id=body.source_warehouse_id,
        destination_warehouse_id=body.destination_warehouse_id,
        status="DRAFT",
        requested_by_id=current_user.id,
        items=items_to_add
    )
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    logger.info("stock_transfer_request_created", transfer_number=tf_num)
    return transfer

@router.post("/{id}/approve", response_model=StockTransferResponse, summary="Approve stock transfer")
async def approve_transfer(
    id: UUID,
    body: ApprovalWorkflowAction,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> StockTransfer:
    query = select(StockTransfer).where(and_(StockTransfer.id == id, StockTransfer.deleted_at.is_(None))).options(
        selectinload(StockTransfer.items)
    )
    res = await db.execute(query)
    transfer = res.scalars().first()
    if not transfer:
        raise EntityNotFoundException("Stock Transfer not found")
        
    if transfer.status != "DRAFT":
        raise ValidationException("Only draft transfers can be approved")

    transfer.status = "PENDING_APPROVAL" if not body.approved else "IN_TRANSIT"
    transfer.approved_by_id = current_user.id if body.approved else None
    
    # If approved (which means ready to ship / in-transit), reserve stock in source warehouse
    if body.approved:
        inv_repo = InventoryRepository(db)
        for item in transfer.items:
            success = await inv_repo.reserve_stock(
                warehouse_id=transfer.source_warehouse_id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id
            )
            if not success:
                raise ValidationException(f"Insufficient stock in source warehouse for product: {item.product_id}")
                
        transfer.status = "IN_TRANSIT"

    await db.commit()
    await db.refresh(transfer)
    logger.info("stock_transfer_approved_status", id=str(id), status=transfer.status)
    return transfer

@router.post("/{id}/receive", response_model=StockTransferResponse, summary="Receive stock transfer at destination")
async def receive_transfer(
    id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "WAREHOUSE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> StockTransfer:
    query = select(StockTransfer).where(and_(StockTransfer.id == id, StockTransfer.deleted_at.is_(None))).options(
        selectinload(StockTransfer.items)
    )
    res = await db.execute(query)
    transfer = res.scalars().first()
    if not transfer:
        raise EntityNotFoundException("Stock Transfer not found")
        
    if transfer.status != "IN_TRANSIT":
        raise ValidationException("Can only receive transfers that are currently in-transit")

    inv_repo = InventoryRepository(db)
    for item in transfer.items:
        # 1. Deduct from source warehouse (on_hand and reserved)
        src_inv = await inv_repo.get_or_create_inventory(transfer.source_warehouse_id, item.product_id, item.variant_id)
        src_inv.quantity_on_hand -= item.quantity
        src_inv.quantity_reserved -= item.quantity
        src_inv.quantity_available = src_inv.quantity_on_hand - src_inv.quantity_reserved
        
        # Log outbound transaction for source warehouse
        src_txn = InventoryTransaction(
            inventory_id=src_inv.id,
            transaction_type="TRANSFER",
            quantity=-item.quantity,
            reference_document=transfer.transfer_number,
            cost_price=src_inv.product.cost_price if src_inv.product else 0.0,
            user_id=current_user.id,
            notes=f"Transferred to warehouse {transfer.destination_warehouse_id}"
        )
        db.add(src_txn)
        
        # 2. Add to destination warehouse
        dest_inv = await inv_repo.get_or_create_inventory(transfer.destination_warehouse_id, item.product_id, item.variant_id)
        dest_inv.quantity_on_hand += item.quantity
        dest_inv.quantity_available = dest_inv.quantity_on_hand - dest_inv.quantity_reserved
        
        # Log inbound transaction for destination warehouse
        dest_txn = InventoryTransaction(
            inventory_id=dest_inv.id,
            transaction_type="TRANSFER",
            quantity=item.quantity,
            reference_document=transfer.transfer_number,
            cost_price=dest_inv.product.cost_price if dest_inv.product else 0.0,
            user_id=current_user.id,
            notes=f"Transferred from warehouse {transfer.source_warehouse_id}"
        )
        db.add(dest_txn)

    transfer.status = "COMPLETED"
    await db.commit()
    await db.refresh(transfer)
    logger.info("stock_transfer_completed", transfer_number=transfer.transfer_number)
    return transfer
from sqlalchemy.orm import selectinload
