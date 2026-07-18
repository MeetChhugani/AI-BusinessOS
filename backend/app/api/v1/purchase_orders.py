from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException, PermissionDeniedException
from app.logging.config import logger
from app.models.inventory import (
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceipt,
    Inventory,
    InventoryTransaction,
    ApprovalWorkflow,
)
from app.models.user import User
from app.repositories.inventory_repository import PurchaseOrderRepository, InventoryRepository
from app.schemas.inventory import (
    ApprovalWorkflowAction,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
)

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.get("", response_model=List[PurchaseOrderResponse], summary="List purchase orders")
async def list_purchase_orders(
    status: Optional[str] = None,
    supplier_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
) -> List[PurchaseOrder]:
    repo = PurchaseOrderRepository(db)
    pos, _ = await repo.get_all_paginated(status=status, supplier_id=supplier_id, skip=skip, limit=limit)
    return pos

@router.post("", response_model=PurchaseOrderResponse, status_code=201, summary="Create a purchase order")
async def create_purchase_order(
    body: PurchaseOrderCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "PURCHASE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> PurchaseOrder:
    # 1. Generate PO Number
    count_q = select(func.count(PurchaseOrder.id))
    r_count = await db.execute(count_q)
    total = r_count.scalar() or 0
    po_num = f"PO-{total + 1:04d}"

    # 2. Sum subtotal
    subtotal = 0.0
    items_to_add = []
    for it in body.items:
        cost = it.quantity_ordered * it.unit_price
        subtotal += cost
        items_to_add.append(
            PurchaseOrderItem(
                product_id=it.product_id,
                variant_id=it.variant_id,
                quantity_ordered=it.quantity_ordered,
                unit_price=it.unit_price,
                tax_rate=it.tax_rate,
                total_cost=cost
            )
        )

    total_amount = subtotal + body.tax_amount - body.discount_amount
    
    po = PurchaseOrder(
        po_number=po_num,
        supplier_id=body.supplier_id,
        status="DRAFT",
        subtotal=subtotal,
        tax_amount=body.tax_amount,
        discount_amount=body.discount_amount,
        total_amount=total_amount,
        created_by_id=current_user.id,
        items=items_to_add
    )
    
    repo = PurchaseOrderRepository(db)
    created = await repo.create(po)
    logger.info("purchase_order_draft_created", po_number=po_num)
    return created

@router.post("/{id}/submit", response_model=PurchaseOrderResponse, summary="Submit PO for review")
async def submit_po(
    id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> PurchaseOrder:
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(id)
    if not po:
        raise EntityNotFoundException("Purchase Order not found")
    if po.status != "DRAFT":
        raise ValidationException(f"Cannot submit PO in status {po.status}")

    po.status = "SUBMITTED"
    
    # Auto-assign initial workflow approval step (Assigned to Admin user)
    # Fetch admin user to assign workflow
    admin_q = select(User).where(User.role == "ADMIN")
    res = await db.execute(admin_q)
    admin = res.scalars().first()
    if admin:
        wf = ApprovalWorkflow(
            entity_type="PURCHASE_ORDER",
            entity_id=po.id,
            approver_id=admin.id,
            sequence_order=1,
            status="PENDING"
        )
        db.add(wf)
        
    await db.commit()
    await db.refresh(po)
    logger.info("purchase_order_submitted", id=str(id))
    return po

@router.post("/{id}/approve", response_model=PurchaseOrderResponse, summary="Approve or Reject PO")
async def approve_po(
    id: UUID,
    body: ApprovalWorkflowAction,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> PurchaseOrder:
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(id)
    if not po:
        raise EntityNotFoundException("Purchase Order not found")
    if po.status != "SUBMITTED":
        raise ValidationException("Only submitted Purchase Orders can be approved")

    # Fetch active workflow step
    wf_q = select(ApprovalWorkflow).where(
        and_(
            ApprovalWorkflow.entity_type == "PURCHASE_ORDER",
            ApprovalWorkflow.entity_id == po.id,
            ApprovalWorkflow.status == "PENDING"
        )
    )
    res = await db.execute(wf_q)
    wf = res.scalars().first()
    
    if wf:
        wf.status = "APPROVED" if body.approved else "REJECTED"
        wf.comments = body.comments
        wf.reviewed_at = func.now()
        
    po.status = "APPROVED" if body.approved else "CANCELLED"
    
    # If approved, increment quantity_incoming in target warehouses (illustratively target warehouse 1)
    if body.approved:
        # We find or initialize items in inventory and add to quantity_incoming
        pass
        
    await db.commit()
    await db.refresh(po)
    logger.info("purchase_order_reviewed", id=str(id), approved=body.approved)
    return po

@router.post("/{id}/receive", response_model=PurchaseOrderResponse, summary="Receive Goods Receipt items")
async def receive_po(
    id: UUID,
    warehouse_id: UUID,
    notes: Optional[str] = None,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "WAREHOUSE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> PurchaseOrder:
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(id)
    if not po:
        raise EntityNotFoundException("Purchase Order not found")
    if po.status != "APPROVED":
        raise ValidationException("Can only receive approved Purchase Orders")

    # Generate GRN number
    count_grn = select(func.count(GoodsReceipt.id))
    r_c = await db.execute(count_grn)
    total = r_c.scalar() or 0
    grn_num = f"GRN-{total + 1:04d}"

    # Log GoodsReceipt metadata
    receipt = GoodsReceipt(
        grn_number=grn_num,
        purchase_order_id=po.id,
        warehouse_id=warehouse_id,
        received_by_id=current_user.id,
        notes=notes
    )
    db.add(receipt)

    # Process items and log stock transaction entries
    inv_repo = InventoryRepository(db)
    for item in po.items:
        # Mark as received
        item.quantity_received = item.quantity_ordered
        
        # Log stock inbound movement
        await inv_repo.log_stock_movement(
            warehouse_id=warehouse_id,
            product_id=item.product_id,
            quantity=item.quantity_ordered,
            transaction_type="INBOUND",
            user_id=current_user.id,
            variant_id=item.variant_id,
            reference_document=grn_num,
            cost_price=item.unit_price,
            notes=f"Goods Receipt matching {po.po_number}"
        )

    po.status = "RECEIVED"
    await db.commit()
    await db.refresh(po)
    logger.info("purchase_order_goods_received", po_number=po.po_number, grn_number=grn_num)
    return po
