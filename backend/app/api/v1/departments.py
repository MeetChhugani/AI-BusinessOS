from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.hcm import Department
from app.repositories.hcm_repository import DepartmentRepository
from app.schemas.hcm import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("", response_model=List[DepartmentResponse], summary="List all active departments")
async def list_departments(
    db: AsyncSession = Depends(get_db_session)
) -> List[Department]:
    dept_repo = DepartmentRepository(db)
    return await dept_repo.get_all()

@router.get("/stats", summary="Get department employee headcount and budget statistics")
async def get_department_stats(
    db: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    dept_repo = DepartmentRepository(db)
    return await dept_repo.get_headcount_stats()

@router.post("", response_model=DepartmentResponse, status_code=201, summary="Create a new department")
async def create_department(
    body: DepartmentCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> Department:
    dept_repo = DepartmentRepository(db)
    new_dept = Department(
        name=body.name,
        description=body.description,
        head_id=body.head_id,
        budget=body.budget,
        status=body.status,
    )
    created = await dept_repo.create(new_dept)
    logger.info("department_created", name=created.name)
    return created

@router.put("/{id}", response_model=DepartmentResponse, summary="Update department settings")
async def update_department(
    id: UUID,
    body: DepartmentCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> Department:
    dept_repo = DepartmentRepository(db)
    dept = await dept_repo.get_by_id(id)
    if not dept:
        raise EntityNotFoundException("Department not found")
        
    dept.name = body.name
    dept.description = body.description
    dept.head_id = body.head_id
    dept.budget = body.budget
    dept.status = body.status
    
    updated = await dept_repo.update(dept)
    logger.info("department_updated", name=updated.name)
    return updated
