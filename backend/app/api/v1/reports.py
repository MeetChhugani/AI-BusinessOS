from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.repositories.finance_repository import FinancialReportRepository

router = APIRouter(prefix="/reports", tags=["Financial Reports"])

@router.get("/trial-balance", summary="Generate Trial Balance Report")
async def get_trial_balance(
    db: AsyncSession = Depends(get_db_session)
):
    repo = FinancialReportRepository(db)
    return await repo.get_trial_balance()

@router.get("/profit-loss", summary="Generate Profit & Loss Statement")
async def get_profit_loss(
    db: AsyncSession = Depends(get_db_session)
):
    repo = FinancialReportRepository(db)
    return await repo.get_profit_loss()
