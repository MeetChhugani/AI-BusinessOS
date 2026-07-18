from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.models.notifications import NotificationTemplate

router = APIRouter(prefix="/email", tags=["Email Engine"])

@router.get("/templates", summary="List email templates")
async def list_templates(
    db: AsyncSession = Depends(get_db_session)
):
    query = select(NotificationTemplate).where(NotificationTemplate.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())
