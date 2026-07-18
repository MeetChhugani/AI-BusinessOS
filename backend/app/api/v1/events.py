from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.models.events import SystemEvent
from app.schemas.platform import SystemEventResponse

router = APIRouter(prefix="/events", tags=["System Event Monitor"])

@router.get("", response_model=List[SystemEventResponse], summary="List processed system events history")
async def list_events(
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
) -> List[SystemEvent]:
    query = select(SystemEvent).order_by(SystemEvent.created_at.desc())
    res = await db.execute(query)
    return list(res.scalars().all())
