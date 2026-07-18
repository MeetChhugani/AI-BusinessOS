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
    InventoryAudit,
    InventoryAuditItem,
    Inventory,
    StockAdjustment,
    InventoryTransaction,
)
from app.repositories.inventory_repository import InventoryRepository

router = APIRouter(prefix="/audits", tags=["Audits"])

@router.get("", summary="List all cycle counts audits")
async def list_audits(
    warehouse_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(InventoryAudit).where(InventoryAudit.deleted_at.is_(None)).options(
        selectinload(InventoryAudit.items)
    )
    if warehouse_id:
        query = query.where(InventoryAudit.warehouse_id == warehouse_id)
    result = await db.execute(query.order_by(InventoryAudit.created_at.desc()))
    return list(result.scalars().all())

@router.post("", status_code=201, summary="Schedule a new inventory audit cycle count")
async def schedule_audit(
    warehouse_id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
):
    # Generate audit number
    count_q = select(func.count(InventoryAudit.id))
    r_c = await db.execute(count_q)
    total = r_c.scalar() or 0
    audit_num = f"AUD-{total + 1:04d}"

    audit = InventoryAudit(
        audit_number=audit_num,
        warehouse_id=warehouse_id,
        status="SCHEDULED",
        started_at=func.now(),
        audited_by_id=current_user.id
    )
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    logger.info("inventory_audit_scheduled", audit_number=audit_num)
    return audit

@router.post("/{id}/count", summary="Record a counted item quantity")
async def record_physical_count(
    id: UUID,
    inventory_id: UUID,
    physical_qty: float,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "WAREHOUSE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
):
    query = select(InventoryAudit).where(and_(InventoryAudit.id == id, InventoryAudit.deleted_at.is_(None)))
    res = await db.execute(query)
    audit = res.scalars().first()
    if not audit:
        raise EntityNotFoundException("Inventory Audit not found")
        
    # Fetch system inventory details
    inv_q = select(Inventory).where(Inventory.id == inventory_id)
    inv_res = await db.execute(inv_q)
    inv = inv_res.scalars().first()
    if not inv:
        raise EntityNotFoundException("Inventory item not found")

    system_qty = inv.quantity_on_hand
    variance = physical_qty - system_qty
    
    # Check if audit item log exists already
    item_q = select(InventoryAuditItem).where(
        and_(
            InventoryAuditItem.inventory_audit_id == id,
            InventoryAuditItem.inventory_id == inventory_id
        )
    )
    item_res = await db.execute(item_q)
    item = item_res.scalars().first()
    
    if not item:
        item = InventoryAuditItem(
            inventory_audit_id=id,
            inventory_id=inventory_id,
            system_quantity=system_qty,
            physical_quantity=physical_qty,
            variance=variance,
            status="DISCREPANCY" if variance != 0.0 else "MATCHED"
        )
        db.add(item)
    else:
        item.physical_quantity = physical_qty
        item.variance = variance
        item.status = "DISCREPANCY" if variance != 0.0 else "MATCHED"

    audit.status = "IN_PROGRESS"
    await db.commit()
    return item

@router.post("/{id}/commit", summary="Commit cycle count reconciliations")
async def commit_audit(
    id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
):
    query = select(InventoryAudit).where(and_(InventoryAudit.id == id, InventoryAudit.deleted_at.is_(None))).options(
        selectinload(InventoryAudit.items)
    )
    res = await db.execute(query)
    audit = res.scalars().first()
    if not audit:
        raise EntityNotFoundException("Inventory Audit not found")
        
    if audit.status == "COMPLETED":
        raise ValidationException("Audit is already completed and committed")

    # Run reconciliations (adjust system inventory stock level for items with variance discrepancies)
    inv_repo = InventoryRepository(db)
    for item in audit.items:
        if item.variance != 0.0:
            inv_q = select(Inventory).where(Inventory.id == item.inventory_id)
            inv_res = await db.execute(inv_q)
            inv = inv_res.scalars().first()
            if inv:
                # Update inventory stock levels
                inv.quantity_on_hand = item.physical_quantity
                inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
                
                # Log adjustment records
                adj_q = select(func.count(StockAdjustment.id))
                adj_c = await db.execute(adj_q)
                adj_tot = adj_c.scalar() or 0
                adj_number = f"ADJ-AUD-{adj_tot + 1:04d}"
                
                adj = StockAdjustment(
                    adjustment_number=adj_number,
                    warehouse_id=audit.warehouse_id,
                    inventory_id=inv.id,
                    original_quantity=item.system_quantity,
                    new_quantity=item.physical_quantity,
                    variance=item.variance,
                    reason=f"Inventory Audit reconciliation {audit.audit_number}",
                    adjusted_by_id=current_user.id
                )
                db.add(adj)
                
                # Create transactions logs
                txn = InventoryTransaction(
                    inventory_id=inv.id,
                    transaction_type="ADJUSTMENT",
                    quantity=item.variance,
                    reference_document=audit.audit_number,
                    cost_price=inv.product.cost_price if inv.product else 0.0,
                    user_id=current_user.id,
                    notes=f"Audit correction {audit.audit_number}"
                )
                db.add(txn)
                
                item.status = "CORRECTED"

    audit.status = "COMPLETED"
    audit.completed_at = func.now()
    await db.commit()
    logger.info("inventory_audit_committed", audit_number=audit.audit_number)
    return {"success": True, "message": f"Inventory audit {audit.audit_number} reconciliations committed successfully"}
from sqlalchemy.orm import selectinload
