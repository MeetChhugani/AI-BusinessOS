from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.crm import Opportunity, OpportunityProduct, CustomerActivityLog
from app.schemas.crm import OpportunityCreate, OpportunityResponse

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("", response_model=List[OpportunityResponse], summary="List opportunities")
async def list_opportunities(
    stage: Optional[str] = None,
    assigned_to_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[Opportunity]:
    query = select(Opportunity).where(Opportunity.deleted_at.is_(None)).options(
        selectinload(Opportunity.products)
    )
    if stage:
        query = query.where(Opportunity.stage == stage)
    if assigned_to_id:
        query = query.where(Opportunity.assigned_to_id == assigned_to_id)
        
    result = await db.execute(query)
    return list(result.scalars().all())

@router.post("", response_model=OpportunityResponse, status_code=201, summary="Create an opportunity")
async def create_opportunity(
    body: OpportunityCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER", "SALES_EXECUTIVE"])),
    db: AsyncSession = Depends(get_db_session)
) -> Opportunity:
    # Set default probability based on starting stage
    probabilities = {
        "PROSPECTING": 10.0,
        "QUALIFICATION": 20.0,
        "PROPOSAL": 50.0,
        "NEGOTIATION": 75.0,
        "WON": 100.0,
        "LOST": 0.0
    }
    prob = probabilities.get(body.stage, 10.0)

    products_list = []
    if body.products:
        for p in body.products:
            products_list.append(
                OpportunityProduct(
                    product_id=p.product_id,
                    quantity=p.quantity,
                    unit_price=p.unit_price
                )
            )

    opp = Opportunity(
        name=body.name,
        customer_id=body.customer_id,
        stage=body.stage,
        probability=prob,
        expected_revenue=body.expected_revenue,
        close_date=body.close_date,
        risk_level=body.risk_level,
        competitors=body.competitors,
        assigned_to_id=body.assigned_to_id or current_user.id,
        products=products_list
    )
    db.add(opp)
    await db.flush()

    # Log Customer Activity event
    act = CustomerActivityLog(
        customer_id=body.customer_id,
        activity_type="OPPORTUNITY_CHANGED",
        description=f"New Opportunity '{body.name}' created in stage '{body.stage}'",
        created_by_id=current_user.id
    )
    db.add(act)
    await db.commit()
    await db.refresh(opp)
    logger.info("opportunity_created", name=opp.name)
    return opp

@router.post("/{id}/stage", response_model=OpportunityResponse, summary="Update opportunity pipeline stage")
async def update_opportunity_stage(
    id: UUID,
    stage: str,
    lost_reason: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Opportunity:
    query = select(Opportunity).where(and_(Opportunity.id == id, Opportunity.deleted_at.is_(None))).options(
        selectinload(Opportunity.products)
    )
    res = await db.execute(query)
    opp = res.scalars().first()
    if not opp:
        raise EntityNotFoundException("Opportunity not found")
        
    probabilities = {
        "PROSPECTING": 10.0,
        "QUALIFICATION": 20.0,
        "PROPOSAL": 50.0,
        "NEGOTIATION": 75.0,
        "WON": 100.0,
        "LOST": 0.0
    }
    
    if stage not in probabilities:
        raise ValidationException("Invalid pipeline stage code")
        
    old_stage = opp.stage
    opp.stage = stage
    opp.probability = probabilities[stage]
    if stage == "LOST":
        opp.lost_reason = lost_reason

    # Recalculate Expected Revenue
    # For Won, expected_revenue = total opportunity value, else factor by probability
    # If products exist, sum them up
    total_val = 0.0
    for p in opp.products:
        total_val += (p.quantity * p.unit_price)
        
    if total_val > 0.0:
        opp.expected_revenue = total_val * (opp.probability / 100.0)

    # Log Customer Activity event
    act = CustomerActivityLog(
        customer_id=opp.customer_id,
        activity_type="OPPORTUNITY_CHANGED",
        description=f"Opportunity '{opp.name}' stage shifted from '{old_stage}' to '{stage}'",
        created_by_id=current_user.id
    )
    db.add(act)
    await db.commit()
    await db.refresh(opp)
    logger.info("opportunity_stage_updated", id=str(id), stage=stage)
    return opp
from sqlalchemy.orm import selectinload
