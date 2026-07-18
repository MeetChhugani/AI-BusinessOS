from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.logging.config import logger
from app.models.finance import Budget, BudgetLine
from app.schemas.finance import BudgetCreate, BudgetResponse

router = APIRouter(prefix="/budgets", tags=["Budgeting & Cost Centers"])

@router.get("", response_model=List[BudgetResponse], summary="List budgets")
async def list_budgets(
    db: AsyncSession = Depends(get_db_session)
) -> List[Budget]:
    query = select(Budget).where(Budget.deleted_at.is_(None)).options(
        selectinload(Budget.lines)
    )
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=BudgetResponse, status_code=201, summary="Establish budget limits")
async def create_budget(
    body: BudgetCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Budget:
    lines = []
    for line in body.lines:
        lines.append(
            BudgetLine(
                account_id=line.account_id,
                allocated_amount=line.allocated_amount,
                actual_amount=0.0
            )
        )

    budget = Budget(
        name=body.name,
        cost_center_id=body.cost_center_id,
        start_date=body.start_date,
        end_date=body.end_date,
        status="ACTIVE",
        lines=lines
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    logger.info("budget_plan_created", name=budget.name)
    return budget
