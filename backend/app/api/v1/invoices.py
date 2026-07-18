from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.logging.config import logger
from app.models.finance import CustomerInvoice, InvoiceItem
from app.repositories.finance_repository import InvoiceRepository
from app.schemas.finance import CustomerInvoiceCreate, CustomerInvoiceResponse

router = APIRouter(prefix="/invoices", tags=["Customer Invoices"])

@router.get("", response_model=List[CustomerInvoiceResponse], summary="List invoices")
async def list_invoices(
    customer_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[CustomerInvoice]:
    query = select(CustomerInvoice).where(CustomerInvoice.deleted_at.is_(None)).options(
        selectinload(CustomerInvoice.items)
    )
    if customer_id:
        query = query.where(CustomerInvoice.customer_id == customer_id)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/from-sales-order/{sales_order_id}", response_model=CustomerInvoiceResponse, status_code=201, summary="Generate invoice from Sales Order")
async def generate_invoice(
    sales_order_id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER", "ACCOUNTS_RECEIVABLE"])),
    db: AsyncSession = Depends(get_db_session)
) -> CustomerInvoice:
    repo = InvoiceRepository(db)
    invoice = await repo.create_from_sales_order(sales_order_id)
    return invoice
