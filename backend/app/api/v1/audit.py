from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.models.audit import AuditEvent
from app.schemas.platform import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["Audit Center"])

@router.get("", response_model=List[AuditEventResponse], summary="Retrieve chronological system audit logs")
async def list_audit_logs(
    entity_name: Optional[str] = None,
    source: Optional[str] = None,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
) -> List[AuditEvent]:
    query = select(AuditEvent).order_by(AuditEvent.created_at.desc())
    if entity_name:
        query = query.where(AuditEvent.entity_name == entity_name)
    if source:
        query = query.where(AuditEvent.source == source)
    res = await db.execute(query)
    return list(res.scalars().all())
