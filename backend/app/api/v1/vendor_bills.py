from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.finance import VendorBill, VendorBillItem, JournalEntry, JournalEntryLine
from app.repositories.finance_repository import LedgerRepository, JournalRepository
from app.schemas.finance import VendorBillCreate, VendorBillResponse

router = APIRouter(prefix="/vendor-bills", tags=["Vendor Bills"])

@router.get("", response_model=List[VendorBillResponse], summary="List vendor bills")
async def list_bills(
    db: AsyncSession = Depends(get_db_session)
) -> List[VendorBill]:
    query = select(VendorBill).where(VendorBill.deleted_at.is_(None)).options(
        selectinload(VendorBill.items)
    )
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/from-purchase-order/{purchase_order_id}", response_model=VendorBillResponse, status_code=201, summary="Generate bill from Purchase Order")
async def generate_bill(
    purchase_order_id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER", "ACCOUNTS_PAYABLE"])),
    db: AsyncSession = Depends(get_db_session)
) -> VendorBill:
    from app.models.inventory import PurchaseOrder
    po_q = select(PurchaseOrder).where(PurchaseOrder.id == purchase_order_id).options(selectinload(PurchaseOrder.items))
    po_res = await db.execute(po_q)
    po = po_res.scalars().first()
    if not po:
        raise EntityNotFoundException("Purchase Order not found")

    issue_date = date.today()
    due_date = issue_date + timedelta(days=30)

    # Generate bill number
    count_q = select(func.count(VendorBill.id))
    count_res = await db.execute(count_q)
    total = count_res.scalar() or 0
    bill_num = f"BILL-{issue_date.year}-{total + 1:06d}"

    items_list = []
    for item in po.items:
        items_list.append(
            VendorBillItem(
                product_id=item.product_id,
                quantity=item.quantity_ordered,
                unit_price=item.unit_cost,
                total_cost=item.total_cost
            )
        )

    bill = VendorBill(
        bill_number=bill_num,
        supplier_id=po.supplier_id,
        purchase_order_id=po.id,
        bill_date=issue_date,
        due_date=due_date,
        subtotal=po.subtotal,
        tax_amount=po.tax_amount,
        total_amount=po.total_amount,
        outstanding_balance=po.total_amount,
        status="APPROVED",
        items=items_list
    )
    db.add(bill)
    await db.flush()

    # Automatic double entry posting:
    # Inventory Asset (Asset) Debit (+)
    # Accounts Payable (Liability) Credit (+)
    inv_acc = await LedgerRepository(db).get_by_code("1400") # Inventory Asset Account
    ap_acc = await LedgerRepository(db).get_by_code("2000") # Accounts Payable Account

    if inv_acc and ap_acc:
        je_lines = [
            JournalEntryLine(account_id=inv_acc.id, debit=bill.total_amount, credit=0.0),
            JournalEntryLine(account_id=ap_acc.id, debit=0.0, credit=bill.total_amount)
        ]
        je = JournalEntry(
            entry_date=issue_date,
            description=f"Automated entry for vendor bill {bill_num}",
            source_document=bill_num,
            lines=je_lines
        )
        await JournalRepository(db).post_entry(je)

    await db.commit()
    await db.refresh(bill)
    return bill
from datetime import date, timedelta
