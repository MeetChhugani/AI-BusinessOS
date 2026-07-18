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
from app.models.crm import Customer, Quotation, QuotationItem
from app.models.inventory import ApprovalWorkflow
from app.repositories.crm_repository import PricingEngineRepository
from app.schemas.crm import QuotationCreate, QuotationResponse
from app.schemas.inventory import ApprovalWorkflowAction

router = APIRouter(prefix="/quotations", tags=["Quotations"])

@router.get("", response_model=List[QuotationResponse], summary="List quotations")
async def list_quotations(
    customer_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[Quotation]:
    query = select(Quotation).where(Quotation.deleted_at.is_(None)).options(
        selectinload(Quotation.items)
    )
    if customer_id:
        query = query.where(Quotation.customer_id == customer_id)
        
    result = await db.execute(query.order_by(desc(Quotation.created_at)))
    return list(result.scalars().all())

@router.post("", response_model=QuotationResponse, status_code=201, summary="Generate a quotation with Pricing Engine discounts")
async def create_quotation(
    body: QuotationCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Quotation:
    # 1. Fetch customer details to extract segment (e.g. VIP)
    cust_q = select(Customer).where(Customer.id == body.customer_id)
    cust_res = await db.execute(cust_q)
    customer = cust_res.scalars().first()
    if not customer:
        raise EntityNotFoundException("Customer not found")

    pricing_repo = PricingEngineRepository(db)
    
    # 2. Add items and calculate automatic discounts
    subtotal = 0.0
    items_list = []
    for it in body.items:
        # Call Pricing Engine
        disc_pct = await pricing_repo.get_applicable_discount(customer.segment, it.product_id)
        
        # Apply discount to unit_price
        discounted_price = it.unit_price * (1.0 - (disc_pct / 100.0))
        item_cost = it.quantity * discounted_price
        subtotal += item_cost
        
        items_list.append(
            QuotationItem(
                product_id=it.product_id,
                quantity=it.quantity,
                unit_price=discounted_price,
                tax_rate=18.0, # default 18% GST
                total_cost=item_cost
            )
        )

    # Generate Quotation number
    count_q = select(func.count(Quotation.id))
    r_c = await db.execute(count_q)
    total = r_c.scalar() or 0
    q_num = f"QTN-{total + 1:04d}"

    tax_amount = subtotal * 0.18
    total_amount = subtotal + tax_amount - body.discount_amount

    quote = Quotation(
        quotation_number=q_num,
        opportunity_id=body.opportunity_id,
        customer_id=body.customer_id,
        status="DRAFT",
        version=1,
        valid_until=body.valid_until,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=body.discount_amount,
        total_amount=total_amount,
        created_by_id=current_user.id,
        items=items_list
    )
    
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    logger.info("quotation_created_via_pricing_engine", quotation_number=q_num, discount_pct=disc_pct)
    return quote

@router.post("/{id}/submit", response_model=QuotationResponse, summary="Submit quotation for review")
async def submit_quotation(
    id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Quotation:
    query = select(Quotation).where(and_(Quotation.id == id, Quotation.deleted_at.is_(None))).options(
        selectinload(Quotation.items)
    )
    res = await db.execute(query)
    quote = res.scalars().first()
    if not quote:
        raise EntityNotFoundException("Quotation not found")
        
    if quote.status != "DRAFT":
        raise ValidationException("Quotation is not in draft status")

    quote.status = "SUBMITTED"
    
    # Auto-assign initial workflow approval step (Assigned to Admin user)
    # Fetch admin user to assign workflow
    admin_q = select(User).where(User.role == "ADMIN")
    adm_res = await db.execute(admin_q)
    admin = adm_res.scalars().first()
    if admin:
        from app.models.inventory import ApprovalWorkflow
        wf = ApprovalWorkflow(
            entity_type="QUOTATION",
            entity_id=quote.id,
            approver_id=admin.id,
            sequence_order=1,
            status="PENDING"
        )
        db.add(wf)
        
    await db.commit()
    await db.refresh(quote)
    return quote
from sqlalchemy import desc
from app.models.user import User
