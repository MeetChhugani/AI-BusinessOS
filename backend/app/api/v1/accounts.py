from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.logging.config import logger
from app.models.finance import GeneralLedgerAccount
from app.repositories.finance_repository import LedgerRepository
from app.schemas.finance import GeneralLedgerAccountCreate, GeneralLedgerAccountResponse

router = APIRouter(prefix="/accounts", tags=["Chart of Accounts"])

@router.get("", response_model=List[GeneralLedgerAccountResponse], summary="List GL accounts")
async def list_accounts(
    db: AsyncSession = Depends(get_db_session)
) -> List[GeneralLedgerAccount]:
    repo = LedgerRepository(db)
    return await repo.get_accounts()

@router.post("", response_model=GeneralLedgerAccountResponse, status_code=201, summary="Create a GL account")
async def create_account(
    body: GeneralLedgerAccountCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> GeneralLedgerAccount:
    acc = GeneralLedgerAccount(
        code=body.code,
        name=body.name,
        account_type=body.account_type,
        parent_id=body.parent_id,
        opening_balance=body.opening_balance,
        current_balance=body.opening_balance,
        status=body.status
    )
    repo = LedgerRepository(db)
    created = await repo.create_account(acc)
    logger.info("gl_account_created", code=created.code, name=created.name)
    return created
