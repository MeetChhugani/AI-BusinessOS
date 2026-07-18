from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.logging.config import logger
from app.models.finance import JournalEntry, JournalEntryLine
from app.repositories.finance_repository import JournalRepository
from app.schemas.finance import JournalEntryCreate, JournalEntryResponse

router = APIRouter(prefix="/journal", tags=["Journal Entries"])

@router.get("", response_model=List[JournalEntryResponse], summary="List journal entries")
async def list_journals(
    db: AsyncSession = Depends(get_db_session)
) -> List[JournalEntry]:
    query = select(JournalEntry).where(JournalEntry.deleted_at.is_(None)).options(
        selectinload(JournalEntry.lines)
    )
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=JournalEntryResponse, status_code=201, summary="Post double-entry journal")
async def post_journal(
    body: JournalEntryCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER", "ACCOUNTANT"])),
    db: AsyncSession = Depends(get_db_session)
) -> JournalEntry:
    lines = []
    for line in body.lines:
        lines.append(
            JournalEntryLine(
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                cost_center_id=line.cost_center_id,
                department_id=line.department_id,
                project_id=line.project_id,
                region=line.region
            )
        )

    je = JournalEntry(
        entry_date=body.entry_date,
        description=body.description,
        source_document=body.source_document,
        posted_by_id=current_user.id,
        lines=lines
    )

    repo = JournalRepository(db)
    posted = await repo.post_entry(je)
    return posted
