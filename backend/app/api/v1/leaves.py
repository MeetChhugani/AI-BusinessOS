from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import RoleChecker, get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, PermissionDeniedException, ValidationException
from app.logging.config import logger
from app.models.hcm import Employee, LeaveBalance, LeaveRequest, LeaveType
from app.models.user import User
from app.repositories.hcm_repository import EmployeeRepository, LeaveRepository
from app.schemas.hcm import LeaveBalanceResponse, LeaveRequestApproval, LeaveRequestCreate, LeaveRequestResponse

router = APIRouter(prefix="/leaves", tags=["Leaves"])

async def get_active_employee(db: AsyncSession, user_id: UUID) -> Employee:
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(user_id)
    if not emp:
        raise EntityNotFoundException("Employee profile not mapped to this user account")
    return emp

@router.get("/types", summary="List available leave types")
async def get_leave_types(db: AsyncSession = Depends(get_db_session)) -> List[dict]:
    query = select(LeaveType).where(LeaveType.deleted_at.is_(None))
    res = await db.execute(query)
    types = res.scalars().all()
    return [{"id": t.id, "name": t.name, "code": t.code, "days_per_year": t.days_per_year} for t in types]

@router.get("/balances", response_model=List[LeaveBalanceResponse], summary="Get leave balances for the year")
async def get_my_balances(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[LeaveBalance]:
    employee = await get_active_employee(db, current_user.id)
    active_year = year or date.today().year
    
    leave_repo = LeaveRepository(db)
    return await leave_repo.get_balances(employee.id, active_year)

@router.post("/requests", response_model=LeaveRequestResponse, status_code=201, summary="Submit a new leave request")
async def apply_leave(
    body: LeaveRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> LeaveRequest:
    employee = await get_active_employee(db, current_user.id)
    
    # Calculate duration
    if body.end_date < body.start_date:
        raise ValidationException("End date cannot precede start date")
        
    duration = (body.end_date - body.start_date).days + 1
    
    # Check leave type validity
    query = select(LeaveType).where(and_(LeaveType.id == body.leave_type_id, LeaveType.deleted_at.is_(None)))
    res = await db.execute(query)
    ltype = res.scalars().first()
    if not ltype:
        raise EntityNotFoundException("Leave type not found")
        
    # Check balance
    year = body.start_date.year
    bal_query = select(LeaveBalance).where(
        and_(
            LeaveBalance.employee_id == employee.id,
            LeaveBalance.leave_type_id == body.leave_type_id,
            LeaveBalance.year == year,
            LeaveBalance.deleted_at.is_(None)
        )
    )
    r_bal = await db.execute(bal_query)
    balance = r_bal.scalars().first()
    
    if not balance:
        # Auto-create basic balance from leave type configuration
        balance = LeaveBalance(
            employee_id=employee.id,
            leave_type_id=body.leave_type_id,
            entitled=float(ltype.days_per_year),
            used=0.0,
            pending=0.0,
            year=year
        )
        db.add(balance)
        await db.commit()
        await db.refresh(balance)

    if (balance.entitled - balance.used - balance.pending) < duration:
        raise ValidationException(f"Insufficient leave balance. Requested: {duration} days.")

    # Deduct pending balance
    balance.pending += float(duration)
    
    leave_repo = LeaveRepository(db)
    new_req = LeaveRequest(
        employee_id=employee.id,
        leave_type_id=body.leave_type_id,
        start_date=body.start_date,
        end_date=body.end_date,
        reason=body.reason,
        status="PENDING_MANAGER" if employee.manager_id else "PENDING_HR" # Fallback if no manager assigned
    )
    
    created = await leave_repo.create_request(new_req)
    await leave_repo.update_balance(balance)
    
    logger.info("leave_request_submitted", employee_id=str(employee.id), duration=duration)
    return created

@router.get("/requests", response_model=List[LeaveRequestResponse], summary="List leaves requests")
async def list_leave_requests(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[LeaveRequest]:
    leave_repo = LeaveRepository(db)
    
    if current_user.role in ("SUPER_ADMIN", "ADMIN", "HR"):
        return await leave_repo.get_all_requests_paginated(status=status, skip=skip, limit=limit)
        
    if current_user.role == "MANAGER":
        # Get manager profile ID
        query = select(Employee).where(and_(Employee.user_id == current_user.id, Employee.deleted_at.is_(None)))
        res = await db.execute(query)
        manager = res.scalars().first()
        if not manager:
            return []
        return await leave_repo.get_all_requests_paginated(manager_id=manager.id, status=status, skip=skip, limit=limit)
        
    # Standard employee sees only own requests
    employee = await get_active_employee(db, current_user.id)
    return await leave_repo.get_all_requests_paginated(employee_id=employee.id, status=status, skip=skip, limit=limit)

@router.post("/requests/{id}/approve", response_model=LeaveRequestResponse, summary="Approve or Reject leave request")
async def approve_leave_request(
    id: UUID,
    body: LeaveRequestApproval,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR", "MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> LeaveRequest:
    leave_repo = LeaveRepository(db)
    req = await leave_repo.get_request_by_id(id)
    if not req:
        raise EntityNotFoundException("Leave request not found")
        
    if req.status in ("APPROVED", "REJECTED", "CANCELLED"):
        raise ValidationException(f"Leave request is already {req.status.lower()}")

    # Fetch reviewer profile if manager
    reviewer_emp = None
    if current_user.role == "MANAGER":
        q = select(Employee).where(and_(Employee.user_id == current_user.id, Employee.deleted_at.is_(None)))
        r = await db.execute(q)
        reviewer_emp = r.scalars().first()
        if not reviewer_emp or req.employee.manager_id != reviewer_emp.id:
            raise PermissionDeniedException("You are not the designated manager for this leave request")

    duration = (req.end_date - req.start_date).days + 1
    
    # Load leave balance record
    year = req.start_date.year
    bal_query = select(LeaveBalance).where(
        and_(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.leave_type_id == req.leave_type_id,
            LeaveBalance.year == year,
            LeaveBalance.deleted_at.is_(None)
        )
    )
    r_bal = await db.execute(bal_query)
    balance = r_bal.scalars().first()
    
    if not balance:
        raise EntityNotFoundException("Leave balance not found")

    if body.approved:
        if req.status == "PENDING_MANAGER":
            req.status = "PENDING_HR"
            req.approved_by_manager_id = reviewer_emp.id if reviewer_emp else None
        elif req.status == "PENDING_HR":
            if current_user.role not in ("SUPER_ADMIN", "ADMIN", "HR"):
                raise PermissionDeniedException("Only HR or Admin can perform final leave approvals")
            req.status = "APPROVED"
            req.approved_by_hr_id = reviewer_emp.id if reviewer_emp else None
            
            # Commit balance deductions
            balance.pending -= float(duration)
            balance.used += float(duration)
    else:
        req.status = "REJECTED"
        req.rejection_reason = body.rejection_reason
        
        # Restore pending balance
        balance.pending -= float(duration)
        
    await leave_repo.update_request(req)
    await leave_repo.update_balance(balance)
    
    logger.info("leave_request_reviewed", req_id=str(req.id), approved=body.approved)
    return req
