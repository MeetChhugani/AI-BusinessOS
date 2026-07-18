from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.models.crm import CRMTask, CRMMeeting
from app.schemas.crm import CRMTaskCreate, CRMTaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=List[CRMTaskResponse], summary="List calendar tasks")
async def list_tasks(
    assigned_to_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[CRMTask]:
    query = select(CRMTask).where(CRMTask.deleted_at.is_(None))
    if assigned_to_id:
        query = query.where(CRMTask.assigned_to_id == assigned_to_id)
    if customer_id:
        query = query.where(CRMTask.customer_id == customer_id)
        
    result = await db.execute(query.order_by(CRMTask.due_date))
    return list(result.scalars().all())

@router.post("", response_model=CRMTaskResponse, status_code=201, summary="Create a calendar follow-up task")
async def create_task(
    body: CRMTaskCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> CRMTask:
    task = CRMTask(
        title=body.title,
        description=body.description,
        due_date=body.due_date,
        priority=body.priority,
        status="PENDING",
        assigned_to_id=current_user.id,
        customer_id=body.customer_id,
        lead_id=body.lead_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("/meetings", summary="List calendar meetings")
async def list_meetings(
    assigned_to_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(CRMMeeting).where(CRMMeeting.deleted_at.is_(None))
    if assigned_to_id:
        query = query.where(CRMMeeting.assigned_to_id == assigned_to_id)
    result = await db.execute(query.order_by(CRMMeeting.start_time))
    return list(result.scalars().all())

@router.post("/meetings", status_code=201, summary="Schedule a calendar meeting")
async def create_meeting(
    title: str,
    description: Optional[str],
    start_time: datetime,
    end_time: datetime,
    location: Optional[str],
    customer_id: Optional[UUID] = None,
    lead_id: Optional[UUID] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    meeting = CRMMeeting(
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        location=location,
        assigned_to_id=current_user.id,
        customer_id=customer_id,
        lead_id=lead_id
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting
