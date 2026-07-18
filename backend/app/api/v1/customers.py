from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.crm import Customer, CustomerContact, CustomerActivityLog
from app.repositories.crm_repository import CustomerRepository
from app.schemas.crm import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=List[CustomerResponse], summary="List customers directory")
async def list_customers(
    search: Optional[str] = None,
    segment: Optional[str] = None,
    industry: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
) -> List[Customer]:
    repo = CustomerRepository(db)
    customers, _ = await repo.get_all_paginated(
        search=search, segment=segment, industry=industry, skip=skip, limit=limit
    )
    return customers

@router.post("", response_model=CustomerResponse, status_code=201, summary="Create a new customer profile")
async def create_customer(
    body: CustomerCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "SALES_DIRECTOR", "SALES_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Customer:
    contacts_list = []
    if body.contacts:
        for contact in body.contacts:
            contacts_list.append(
                CustomerContact(
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    email=contact.email,
                    phone=contact.phone,
                    job_title=contact.job_title,
                    is_primary=contact.is_primary
                )
            )

    new_cust = Customer(
        name=body.name,
        customer_type=body.customer_type,
        gst_number=body.gst_number,
        industry=body.industry,
        segment=body.segment,
        credit_limit=body.credit_limit,
        payment_terms=body.payment_terms,
        territory_id=body.territory_id,
        status=body.status,
        contacts=contacts_list
    )
    
    repo = CustomerRepository(db)
    created = await repo.create(new_cust)
    
    # Log activity note
    act = CustomerActivityLog(
        customer_id=created.id,
        activity_type="NOTE",
        description="Customer account created and primary profiles seeded",
        created_by_id=current_user.id
    )
    db.add(act)
    await db.commit()
    
    logger.info("customer_profile_created", name=created.name)
    return created

@router.get("/{id}/timeline", summary="Get unified customer activity log timeline")
async def get_customer_timeline(
    id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(CustomerActivityLog).where(CustomerActivityLog.customer_id == id).order_by(CustomerActivityLog.created_at.desc())
    res = await db.execute(query)
    return list(res.scalars().all())
