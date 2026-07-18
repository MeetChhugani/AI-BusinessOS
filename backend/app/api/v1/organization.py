from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.models.hcm import Employee

router = APIRouter(prefix="/organization", tags=["Organization"])

@router.get("/chart", summary="Get organizational reporting tree nodes list")
async def get_organization_chart(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[dict]:
    # Query all active employees including designation and department info
    query = (
        select(Employee)
        .where(Employee.deleted_at.is_(None))
        .options(
            selectinload(Employee.designation),
            selectinload(Employee.department),
        )
    )
    result = await db.execute(query)
    employees = result.scalars().all()

    nodes = []
    for emp in employees:
        nodes.append({
            "id": str(emp.id),
            "pid": str(emp.manager_id) if emp.manager_id else None,
            "name": f"{emp.first_name} {emp.last_name}",
            "title": emp.designation.name if emp.designation else "Associate",
            "department": emp.department.name if emp.department else "General Operations",
            "avatar": emp.profile_image or f"https://api.dicebear.com/7.x/initials/svg?seed={emp.first_name}",
            "status": emp.status,
            "employment_type": emp.employment_type,
        })

    return nodes
