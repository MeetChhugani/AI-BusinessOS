import uuid
from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy import and_, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.crm import (
    Customer,
    CustomerContact,
    CustomerAddress,
    CustomerNote,
    CustomerActivityLog,
    Lead,
    LeadActivity,
    Opportunity,
    OpportunityProduct,
    PricingRule,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
    SalesTerritory,
    CRMTask,
    CRMMeeting,
    CRMCommunication,
)
from app.models.user import User
from app.repositories.inventory_repository import InventoryRepository

class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

class CustomerRepository(BaseRepository):
    async def get_all_paginated(
        self,
        search: Optional[str] = None,
        segment: Optional[str] = None,
        industry: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Customer], int]:
        query = select(Customer).where(Customer.deleted_at.is_(None)).options(
            selectinload(Customer.contacts),
            selectinload(Customer.territory)
        )
        if search:
            query = query.where(Customer.name.icontains(search) | Customer.industry.icontains(search))
        if segment:
            query = query.where(Customer.segment == segment)
        if industry:
            query = query.where(Customer.industry == industry)
            
        count_q = select(func.count()).select_from(query.subquery())
        c_res = await self.db.execute(count_q)
        total = c_res.scalar_one() or 0
        
        result = await self.db.execute(query.order_by(Customer.name).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_id(self, id: uuid.UUID) -> Optional[Customer]:
        query = select(Customer).where(and_(Customer.id == id, Customer.deleted_at.is_(None))).options(
            selectinload(Customer.contacts),
            selectinload(Customer.addresses),
            selectinload(Customer.notes),
            selectinload(Customer.activity_logs)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update(self, customer: Customer) -> Customer:
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

class LeadRepository(BaseRepository):
    async def get_all_paginated(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Lead], int]:
        query = select(Lead).where(Lead.deleted_at.is_(None))
        if search:
            query = query.where(Lead.first_name.icontains(search) | Lead.last_name.icontains(search) | Lead.company_name.icontains(search))
        if status:
            query = query.where(Lead.status == status)
        if source:
            query = query.where(Lead.source == source)
            
        count_q = select(func.count()).select_from(query.subquery())
        c_res = await self.db.execute(count_q)
        total = c_res.scalar_one() or 0
        
        result = await self.db.execute(query.order_by(desc(Lead.created_at)).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_id(self, id: uuid.UUID) -> Optional[Lead]:
        query = select(Lead).where(and_(Lead.id == id, Lead.deleted_at.is_(None))).options(
            selectinload(Lead.activities)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def convert_to_customer(self, lead_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Customer]:
        lead = await self.get_by_id(lead_id)
        if not lead or lead.status == "CONVERTED":
            return None
            
        # 1. Create Customer Profile
        customer = Customer(
            name=lead.company_name or f"{lead.first_name} {lead.last_name}",
            customer_type="COMPANY" if lead.company_name else "INDIVIDUAL",
            status="ACTIVE",
            segment="SME"
        )
        self.db.add(customer)
        await self.db.flush()
        
        # 2. Create Primary Contact
        contact = CustomerContact(
            customer_id=customer.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            is_primary=True
        )
        self.db.add(contact)
        
        # Log conversion event note
        note = CustomerNote(
            customer_id=customer.id,
            note=f"Converted from Lead record. Original lead score: {lead.score}",
            created_by_id=user_id
        )
        self.db.add(note)
        
        # Mark lead as converted
        lead.status = "CONVERTED"
        lead.converted_customer_id = customer.id
        
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

class PricingEngineRepository(BaseRepository):
    async def get_applicable_discount(
        self,
        segment: str,
        product_id: uuid.UUID
    ) -> float:
        # Fetch active pricing rules matching segment and optional product_id
        today = date.today()
        query = select(PricingRule).where(
            and_(
                PricingRule.customer_segment == segment,
                PricingRule.status == "ACTIVE",
                PricingRule.start_date <= today,
                PricingRule.end_date >= today
            )
        ).order_by(desc(PricingRule.priority))
        
        res = await self.db.execute(query)
        rules = res.scalars().all()
        
        # Match specific product rules first, fallback to general rules
        for rule in rules:
            if rule.product_id == product_id:
                return rule.discount_percentage
        for rule in rules:
            if rule.product_id is None:
                return rule.discount_percentage
                
        return 0.0

class SalesOrderRepository(BaseRepository):
    async def create(self, order: SalesOrder) -> SalesOrder:
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_by_id(self, id: uuid.UUID) -> Optional[SalesOrder]:
        query = select(SalesOrder).where(and_(SalesOrder.id == id, SalesOrder.deleted_at.is_(None))).options(
            selectinload(SalesOrder.customer),
            selectinload(SalesOrder.items)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def approve_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        order = await self.get_by_id(order_id)
        if not order or order.status != "PENDING_APPROVAL":
            return False
            
        # 1. Update status
        order.status = "APPROVED"
        
        # 2. Integrate with Stock Reservation
        # Fetch central warehouse to allocate reserves (central warehouse code WH-CENTRAL)
        from app.models.inventory import Warehouse
        wh_q = select(Warehouse).where(Warehouse.code == "WH-CENTRAL")
        wh_res = await self.db.execute(wh_q)
        wh = wh_res.scalars().first()
        
        if wh:
            inv_repo = InventoryRepository(self.db)
            for item in order.items:
                # Deduct available stock while keeping total on_hand
                await inv_repo.reserve_stock(
                    warehouse_id=wh.id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    reference_type="SALES_ORDER",
                    reference_id=order.id
                )
                
        await self.db.commit()
        return True
