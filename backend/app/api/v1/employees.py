from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker, get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import PermissionDeniedException, EntityNotFoundException
from app.logging.config import logger
from app.models.hcm import Employee, EmployeeSkill, EmployeeTimeline, SalaryHistory, EmployeeNote
from app.models.user import User
from app.repositories.hcm_repository import EmployeeRepository, SalaryRepository
from app.schemas.hcm import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    EmployeeSkillResponse,
    EmployeeSkillBase,
    SalaryHistoryCreate,
    SalaryHistoryResponse,
    EmployeeTimelineResponse,
    EmployeeNoteCreate,
    EmployeeNoteResponse,
)

router = APIRouter(prefix="/employees", tags=["Employees"])

# Helper function to check if a manager has direct tree access to a target employee
async def verify_manager_tree_access(db: AsyncSession, manager_user_id: UUID, target_employee: Employee) -> bool:
    query = select(Employee).where(and_(Employee.user_id == manager_user_id, Employee.deleted_at.is_(None)))
    res = await db.execute(query)
    manager = res.scalars().first()
    if not manager:
        return False
    if target_employee.manager_id == manager.id:
        return True
    
    curr = target_employee
    visited = set()
    while curr.manager_id is not None:
        if curr.manager_id == manager.id:
            return True
        if curr.manager_id in visited:
            break
        visited.add(curr.manager_id)
        
        q = select(Employee).where(and_(Employee.id == curr.manager_id, Employee.deleted_at.is_(None)))
        r = await db.execute(q)
        curr = r.scalars().first()
        if not curr:
            break
    return False

async def enforce_profile_access(db: AsyncSession, current_user: User, employee_id: UUID) -> Employee:
    emp_repo = EmployeeRepository(db)
    target = await emp_repo.get_by_id(employee_id)
    if not target:
        raise EntityNotFoundException("Employee profile not found")

    if current_user.role in ("SUPER_ADMIN", "ADMIN", "HR"):
        return target
        
    if current_user.role == "MANAGER":
        # Check if the manager is accessing their own employee profile
        if target.user_id == current_user.id:
            return target
        # Check direct report tree
        if await verify_manager_tree_access(db, current_user.id, target):
            return target
        raise PermissionDeniedException("You do not have access to this employee profile")
        
    if current_user.role == "EMPLOYEE":
        if target.user_id != current_user.id:
            raise PermissionDeniedException("You can only access your own profile details")
        return target
        
    raise PermissionDeniedException("Insufficient system permissions")

@router.post("", response_model=EmployeeResponse, status_code=201, summary="Create a new employee profile")
async def create_employee(
    body: EmployeeCreate,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> Employee:
    emp_repo = EmployeeRepository(db)
    
    # Generate employee_id
    count_query = select(select(Employee).subquery())
    result = await db.execute(select(select(func.count()).select_from(Employee)))
    total = result.scalar_one() or 0
    generated_id = f"EMP-{total + 1:04d}"

    new_emp = Employee(
        user_id=body.user_id,
        employee_id=generated_id,
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        joining_date=body.joining_date,
        exit_date=body.exit_date,
        status=body.status,
        employment_type=body.employment_type,
        onboarding_status="DRAFT", # Starts as Draft status
        department_id=body.department_id,
        designation_id=body.designation_id,
        manager_id=body.manager_id,
        location=body.location,
        emergency_contact_name=body.emergency_contact_name,
        emergency_contact_phone=body.emergency_contact_phone,
        emergency_contact_relation=body.emergency_contact_relation,
        tags=body.tags,
    )
    
    created = await emp_repo.create(new_emp)
    
    # Track Joined timeline event
    timeline_event = EmployeeTimeline(
        employee_id=created.id,
        event_type="JOINED",
        event_date=datetime.now(timezone.utc),
        title="Joined Company",
        description=f"Employee profile initialized with status Draft",
    )
    db.add(timeline_event)
    
    # Record initial salary if provided
    if body.base_salary is not None:
        salary_history = SalaryHistory(
            employee_id=created.id,
            effective_date=body.joining_date or date.today(),
            base_salary=body.base_salary,
            reason="Initial appointment contract details",
            created_by_id=current_user.id,
        )
        db.add(salary_history)
        
    await db.commit()
    await db.refresh(created)
    logger.info("employee_created", employee_id=created.employee_id, email=created.email)
    return created

@router.get("", response_model=List[EmployeeResponse], summary="Search and list employees directory")
async def list_employees(
    search: Optional[str] = None,
    department_id: Optional[UUID] = None,
    designation_id: Optional[UUID] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    manager_id: Optional[UUID] = None,
    employment_type: Optional[str] = None,
    tag: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = "last_name",
    sort_order: str = "asc",
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR", "MANAGER"])),
    db: AsyncSession = Depends(get_db_session),
) -> List[Employee]:
    emp_repo = EmployeeRepository(db)
    
    # Managers are restricted to direct report searches
    if current_user.role == "MANAGER":
        query = select(Employee).where(and_(Employee.user_id == current_user.id, Employee.deleted_at.is_(None)))
        res = await db.execute(query)
        manager_profile = res.scalars().first()
        if manager_profile:
            manager_id = manager_profile.id

    employees, _ = await emp_repo.get_all_paginated(
        search=search,
        department_id=department_id,
        designation_id=designation_id,
        status=status,
        location=location,
        manager_id=manager_id,
        employment_type=employment_type,
        tag=tag,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return employees

@router.get("/{id}", response_model=EmployeeResponse, summary="Get employee details profile by ID")
async def get_employee(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> Employee:
    return await enforce_profile_access(db, current_user, id)

@router.put("/{id}", response_model=EmployeeResponse, summary="Update employee profile")
async def update_employee(
    id: UUID,
    body: EmployeeUpdate,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> Employee:
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(id)
    if not employee:
        raise EntityNotFoundException("Employee profile not found")

    update_data = body.model_dump(exclude_unset=True)
    
    # Track timeline changes if dept or manager is updated
    if "department_id" in update_data and update_data["department_id"] != employee.department_id:
        tl = EmployeeTimeline(
            employee_id=employee.id,
            event_type="DEPT_CHANGED",
            title="Department Transferred",
            description=f"Transferred to department: {update_data['department_id']}",
        )
        db.add(tl)
        
    for k, v in update_data.items():
        setattr(employee, k, v)

    updated = await emp_repo.update(employee)
    logger.info("employee_updated", employee_id=updated.employee_id)
    return updated

@router.delete("/{id}", summary="Soft delete employee profile")
async def soft_delete_employee(
    id: UUID,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(id)
    if not employee:
        raise EntityNotFoundException("Employee profile not found")
        
    await emp_repo.soft_delete(employee)
    logger.info("employee_soft_deleted", employee_id=employee.employee_id)
    return {"success": True, "message": "Employee profile soft deleted successfully"}

@router.post("/{id}/restore", summary="Restore soft deleted employee profile")
async def restore_employee(
    id: UUID,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(id, include_deleted=True)
    if not employee:
        raise EntityNotFoundException("Employee profile not found")
        
    await emp_repo.restore(employee)
    logger.info("employee_restored", employee_id=employee.employee_id)
    return {"success": True, "message": "Employee profile restored successfully"}

# --- SALARY HISTORY SUB-ROUTES ---
@router.get("/{id}/salary", response_model=List[SalaryHistoryResponse], summary="Get employee salary history details")
async def get_salary_history(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[SalaryHistory]:
    # Enforce profile access checks
    await enforce_profile_access(db, current_user, id)
    
    salary_repo = SalaryRepository(db)
    return await salary_repo.get_history(id)

@router.post("/{id}/salary", response_model=SalaryHistoryResponse, status_code=201, summary="Log a new salary adjustment record")
async def log_salary(
    id: UUID,
    body: SalaryHistoryCreate,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR"])),
    db: AsyncSession = Depends(get_db_session),
) -> SalaryHistory:
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_id(id)
    if not employee:
        raise EntityNotFoundException("Employee profile not found")
        
    salary_repo = SalaryRepository(db)
    new_salary = SalaryHistory(
        employee_id=id,
        effective_date=body.effective_date,
        base_salary=body.base_salary,
        bonus=body.bonus,
        allowance=body.allowance,
        deduction=body.deduction,
        reason=body.reason,
        created_by_id=current_user.id,
    )
    created = await salary_repo.add_history(new_salary)
    
    # Track salary change timeline event
    tl = EmployeeTimeline(
        employee_id=id,
        event_type="SALARY_UPDATED",
        title="Salary Updated",
        description=f"Base salary adjusted to {body.base_salary} (Reason: {body.reason or 'Not Specified'})",
    )
    db.add(tl)
    await db.commit()
    
    logger.info("salary_history_logged", employee_id=str(id), amount=body.base_salary)
    return created

# --- SKILLS SUB-ROUTES ---
@router.post("/{id}/skills", response_model=EmployeeSkillResponse, status_code=201, summary="Add a skill rating")
async def add_skill(
    id: UUID,
    body: EmployeeSkillBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> EmployeeSkill:
    await enforce_profile_access(db, current_user, id)
    
    skill = EmployeeSkill(
        employee_id=id,
        skill_name=body.skill_name,
        proficiency=body.proficiency,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    
    logger.info("skill_added", employee_id=str(id), skill=body.skill_name)
    return skill

# --- TIMELINE SUB-ROUTES ---
@router.get("/{id}/timeline", response_model=List[EmployeeTimelineResponse], summary="Get employee timeline history")
async def get_timeline(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> List[EmployeeTimeline]:
    await enforce_profile_access(db, current_user, id)
    
    query = select(EmployeeTimeline).where(EmployeeTimeline.employee_id == id).order_by(desc(EmployeeTimeline.event_date))
    result = await db.execute(query)
    return list(result.scalars().all())

# --- NOTES SUB-ROUTES ---
@router.get("/{id}/notes", response_model=List[EmployeeNoteResponse], summary="Retrieve HR/Manager profile notes")
async def get_notes(
    id: UUID,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR", "MANAGER"])),
    db: AsyncSession = Depends(get_db_session),
) -> List[EmployeeNote]:
    # Enforce tree check permissions
    await enforce_profile_access(db, current_user, id)
    
    query = select(EmployeeNote).where(EmployeeNote.employee_id == id)
    if current_user.role == "MANAGER":
        # Managers can only see MANAGER and GENERAL notes
        query = query.where(EmployeeNote.note_type.in_(["MANAGER", "GENERAL"]))
        
    result = await db.execute(query.order_by(desc(EmployeeNote.created_at)))
    return list(result.scalars().all())

@router.post("/{id}/notes", response_model=EmployeeNoteResponse, status_code=201, summary="Add a profile note")
async def create_note(
    id: UUID,
    body: EmployeeNoteCreate,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR", "MANAGER"])),
    db: AsyncSession = Depends(get_db_session),
) -> EmployeeNote:
    await enforce_profile_access(db, current_user, id)
    
    if current_user.role == "MANAGER" and body.note_type == "PRIVATE_HR":
        raise PermissionDeniedException("Managers cannot write Private HR notes")
        
    note = EmployeeNote(
        employee_id=id,
        author_id=current_user.id,
        note_type=body.note_type,
        content=body.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    logger.info("note_created", employee_id=str(id), author_id=str(current_user.id))
    return note
from sqlalchemy import func
