from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.logging.config import logger
from app.models.finance import Payment, PaymentAllocation
from app.repositories.finance_repository import PaymentRepository
from app.schemas.finance import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("", response_model=List[PaymentResponse], summary="List payments")
async def list_payments(
    db: AsyncSession = Depends(get_db_session)
) -> List[Payment]:
    query = select(Payment).where(Payment.deleted_at.is_(None)).options(
        selectinload(Payment.allocations)
    )
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=PaymentResponse, status_code=201, summary="Record a payment")
async def record_payment(
    body: PaymentCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER", "ACCOUNTS_RECEIVABLE", "ACCOUNTS_PAYABLE"])),
    db: AsyncSession = Depends(get_db_session)
) -> Payment:
    allocs = []
    for alloc in body.allocations:
        allocs.append(
            PaymentAllocation(
                invoice_id=alloc.invoice_id,
                vendor_bill_id=alloc.vendor_bill_id,
                allocated_amount=alloc.allocated_amount
            )
        )

    pay = Payment(
        payment_type=body.payment_type,
        payment_date=body.payment_date,
        amount=body.amount,
        payment_method=body.payment_method,
        reference_number=body.reference_number,
        allocations=allocs
    )

    repo = PaymentRepository(db)
    created = await repo.record_payment(pay)
    return created
