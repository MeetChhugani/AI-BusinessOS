from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.crm import Lead, LeadActivity, Customer
from app.repositories.crm_repository import LeadRepository
from app.schemas.crm import LeadCreate, LeadResponse, CustomerResponse

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.get("", response_model=List[LeadResponse], summary="List CRM leads")
async def list_leads(
    search: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
) -> List[Lead]:
    repo = LeadRepository(db)
    leads, _ = await repo.get_all_paginated(search=search, status=status, source=source, skip=skip, limit=limit)
    return leads

@router.post("", response_model=LeadResponse, status_code=201, summary="Create a new lead manually")
async def create_lead(
    body: LeadCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER", "SALES_EXECUTIVE"])),
    db: AsyncSession = Depends(get_db_session)
) -> Lead:
    new_lead = Lead(
        first_name=body.first_name,
        last_name=body.last_name,
        company_name=body.company_name,
        email=body.email,
        phone=body.phone,
        source=body.source,
        status=body.status,
        score=body.score,
        assigned_to_id=body.assigned_to_id or current_user.id
    )
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    logger.info("lead_profile_created", company=new_lead.company_name)
    return new_lead

@router.post("/{id}/qualify", response_model=LeadResponse, summary="Perform automated lead qualification score")
async def qualify_lead(
    id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Lead:
    repo = LeadRepository(db)
    lead = await repo.get_by_id(id)
    if not lead:
        raise EntityNotFoundException("Lead not found")
        
    # Calculate score based on lead profile complete parameters
    score = 10.0
    if lead.email and ("@" in lead.email and not lead.email.endswith("gmail.com") and not lead.email.endswith("yahoo.com")):
        score += 40.0  # Business domain email bonus
    if lead.company_name:
        score += 30.0  # Company representation bonus
    if lead.phone:
        score += 20.0  # Contact detail bonus
        
    lead.score = score
    lead.status = "QUALIFIED" if score >= 60.0 else "CONTACTED"
    
    # Log lead qualification activity
    act = LeadActivity(
        lead_id=lead.id,
        activity_type="NOTE",
        details=f"Automated qualification scoring run. Calculated score: {score}%",
        created_by_id=current_user.id
    )
    db.add(act)
    await db.commit()
    await db.refresh(lead)
    return lead

@router.post("/{id}/convert", response_model=CustomerResponse, summary="Convert Lead into Customer and Primary Contact")
async def convert_lead(
    id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Customer:
    repo = LeadRepository(db)
    customer = await repo.convert_to_customer(id, current_user.id)
    if not customer:
        raise ValidationException("Lead is already converted or could not be processed")
        
    logger.info("lead_converted_to_customer", lead_id=str(id), customer_id=str(customer.id))
    return customer
