from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.models.scheduler import ScheduledJob
from app.schemas.platform import ScheduledJobResponse

router = APIRouter(prefix="/jobs", tags=["Background Job Scheduler"])

@router.get("", response_model=List[ScheduledJobResponse], summary="List scheduled background jobs")
async def list_jobs(
    db: AsyncSession = Depends(get_db_session)
) -> List[ScheduledJob]:
    query = select(ScheduledJob).where(ScheduledJob.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/{id}/trigger", summary="Manually trigger scheduled background task")
async def trigger_job(
    id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
):
    q = select(ScheduledJob).where(ScheduledJob.id == id)
    res = await db.execute(q)
    job = res.scalars().first()
    if not job:
        raise EntityNotFoundException("Scheduled job config not found")

    job.last_run_at = datetime.utcnow()
    db.add(job)
    await db.commit()
    return {"status": "SUCCESS", "message": f"Manually triggered job {job.name}"}
from datetime import datetime
