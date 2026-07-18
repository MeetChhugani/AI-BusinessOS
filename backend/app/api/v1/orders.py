from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.crm import SalesOrder, SalesOrderItem, CustomerActivityLog
from app.repositories.crm_repository import SalesOrderRepository
from app.schemas.crm import SalesOrderCreate, SalesOrderResponse, ApprovalWorkflowAction

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("", response_model=List[SalesOrderResponse], summary="List sales orders")
async def list_sales_orders(
    customer_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[SalesOrder]:
    query = select(SalesOrder).where(SalesOrder.deleted_at.is_(None))
    if customer_id:
        query = query.where(SalesOrder.customer_id == customer_id)
    if status:
        query = query.where(SalesOrder.status == status)
        
    result = await db.execute(query.order_by(desc(SalesOrder.created_at)))
    return list(result.scalars().all())

@router.post("", response_model=SalesOrderResponse, status_code=201, summary="Create a new sales order")
async def create_sales_order(
    body: SalesOrderCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> SalesOrder:
    # Generate Order Number
    count_q = select(func.count(SalesOrder.id))
    r_c = await db.execute(count_q)
    total = r_c.scalar() or 0
    order_num = f"SO-{total + 1:04d}"

    subtotal = 0.0
    items_list = []
    for it in body.items:
        cost = it.quantity * it.unit_price
        subtotal += cost
        items_list.append(
            SalesOrderItem(
                product_id=it.product_id,
                variant_id=it.variant_id,
                quantity=it.quantity,
                unit_price=it.unit_price,
                tax_rate=18.0,
                total_cost=cost
            )
        )

    tax_amount = subtotal * 0.18
    total_amount = subtotal + tax_amount - body.discount_amount

    order = SalesOrder(
        order_number=order_num,
        customer_id=body.customer_id,
        quotation_id=body.quotation_id,
        status="DRAFT",
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=body.discount_amount,
        total_amount=total_amount,
        created_by_id=current_user.id,
        salesperson_id=current_user.id,
        shipping_status="PENDING",
        items=items_list
    )
    
    repo = SalesOrderRepository(db)
    created = await repo.create(order)
    logger.info("sales_order_draft_created", order_number=order_num)
    return created

@router.post("/{id}/submit", response_model=SalesOrderResponse, summary="Submit order for approval")
async def submit_order(
    id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> SalesOrder:
    repo = SalesOrderRepository(db)
    order = await repo.get_by_id(id)
    if not order:
        raise EntityNotFoundException("Sales Order not found")
        
    if order.status != "DRAFT":
        raise ValidationException("Order is not in draft status")

    order.status = "PENDING_APPROVAL"
    
    # Auto-assign initial workflow approval step (Assigned to Admin user)
    # Fetch admin user to assign workflow
    admin_q = select(User).where(User.role == "ADMIN")
    adm_res = await db.execute(admin_q)
    admin = adm_res.scalars().first()
    if admin:
        from app.models.inventory import ApprovalWorkflow
        wf = ApprovalWorkflow(
            entity_type="SALES_ORDER",
            entity_id=order.id,
            approver_id=admin.id,
            sequence_order=1,
            status="PENDING"
        )
        db.add(wf)
        
    await db.commit()
    await db.refresh(order)
    return order

@router.post("/{id}/approve", response_model=SalesOrderResponse, summary="Approve sales order and reserve inventory")
async def approve_order(
    id: UUID,
    body: ApprovalWorkflowAction,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> SalesOrder:
    repo = SalesOrderRepository(db)
    order = await repo.get_by_id(id)
    if not order:
        raise EntityNotFoundException("Sales Order not found")
        
    if order.status != "PENDING_APPROVAL":
        raise ValidationException("Order is not pending approval")

    # Fetch active workflow step
    from app.models.inventory import ApprovalWorkflow
    wf_q = select(ApprovalWorkflow).where(
        and_(
            ApprovalWorkflow.entity_type == "SALES_ORDER",
            ApprovalWorkflow.entity_id == order.id,
            ApprovalWorkflow.status == "PENDING"
        )
    )
    res = await db.execute(wf_q)
    wf = res.scalars().first()
    
    if wf:
        wf.status = "APPROVED" if body.approved else "REJECTED"
        wf.comments = body.comments
        wf.reviewed_at = func.now()

    if body.approved:
        # Calls the repository which triggers Stock Reservation!
        success = await repo.approve_order(id, current_user.id)
        if not success:
            raise ValidationException("Failed to approve order or reserve warehouse stock")
    else:
        order.status = "CANCELLED"
        await db.commit()

    # Log Customer Activity event
    act = CustomerActivityLog(
        customer_id=order.customer_id,
        activity_type="OPPORTUNITY_CHANGED",
        description=f"Sales Order '{order.order_number}' review completed. Approved: {body.approved}",
        created_by_id=current_user.id
    )
    db.add(act)
    await db.commit()
    await db.refresh(order)
    logger.info("sales_order_approved_and_stock_allocated", id=str(id), approved=body.approved)
    return order
from sqlalchemy import desc
from app.models.user import User
