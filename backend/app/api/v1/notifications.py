from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.models.notifications import NotificationLog
from app.schemas.platform import NotificationLogResponse

router = APIRouter(prefix="/notifications", tags=["Notification Center"])

@router.get("", response_model=List[NotificationLogResponse], summary="Retrieve recent user notifications")
async def list_notifications(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[NotificationLog]:
    query = select(NotificationLog).where(
        NotificationLog.user_id == current_user.id
    ).order_by(NotificationLog.created_at.desc())
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/{id}/read", response_model=NotificationLogResponse, summary="Mark notification alert as read")
async def mark_read(
    id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> NotificationLog:
    q = select(NotificationLog).where(
        NotificationLog.id == id
    )
    res = await db.execute(q)
    log = res.scalars().first()
    if not log:
        raise EntityNotFoundException("Notification record not found")

    log.read_status = True
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
