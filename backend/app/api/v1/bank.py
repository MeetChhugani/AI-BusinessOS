from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.finance import BankAccount, BankTransaction, Reconciliation

router = APIRouter(prefix="/bank", tags=["Banking & Reconciliation"])

@router.get("/accounts", summary="List bank accounts")
async def list_bank_accounts(
    db: AsyncSession = Depends(get_db_session)
):
    query = select(BankAccount).where(BankAccount.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/transactions", summary="List imported bank statement transactions")
async def list_transactions(
    bank_account_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(BankTransaction).where(BankTransaction.deleted_at.is_(None))
    if bank_account_id:
        query = query.where(BankTransaction.bank_account_id == bank_account_id)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/reconcile", status_code=201, summary="Reconcile bank transaction with journal entry")
async def reconcile_transaction(
    bank_transaction_id: UUID,
    journal_entry_id: UUID,
    reconciled_amount: float,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER", "ACCOUNTANT"])),
    db: AsyncSession = Depends(get_db_session)
):
    tx_q = select(BankTransaction).where(BankTransaction.id == bank_transaction_id)
    tx_res = await db.execute(tx_q)
    tx = tx_res.scalars().first()
    if not tx:
        raise EntityNotFoundException("Bank Transaction not found")

    rec = Reconciliation(
        bank_transaction_id=bank_transaction_id,
        journal_entry_id=journal_entry_id,
        reconciled_amount=reconciled_amount,
        reconciled_date=date.today()
    )
    db.add(rec)

    # Update transaction match status
    tx.reconciliation_status = "MATCHED"
    db.add(tx)

    await db.commit()
    logger.info("bank_transaction_reconciled", tx_id=str(bank_transaction_id), je_id=str(journal_entry_id))
    return {"status": "SUCCESS"}
from datetime import date
