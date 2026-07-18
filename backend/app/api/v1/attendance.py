from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException, PermissionDeniedException
from app.logging.config import logger
from app.models.hcm import Attendance, AttendanceSession, Employee
from app.models.user import User
from app.repositories.hcm_repository import AttendanceRepository, EmployeeRepository
from app.schemas.hcm import AttendanceResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])

async def get_active_employee(db: AsyncSession, user_id: UUID) -> Employee:
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(user_id)
    if not emp:
        raise EntityNotFoundException("Employee profile not mapped to this user account")
    return emp

@router.get("/status", summary="Get active clock state of the employee")
async def get_clock_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    employee = await get_active_employee(db, current_user.id)
    today = date.today()
    
    att_repo = AttendanceRepository(db)
    record = await att_repo.get_day_record(employee.id, today)
    if not record:
        return {"clocked_in": False, "status": "OUT", "session": None}
        
    # Find latest session
    sessions = sorted(record.sessions, key=lambda s: s.clock_in, reverse=True)
    if not sessions:
        return {"clocked_in": False, "status": "OUT", "session": None}
        
    latest = sessions[0]
    if latest.clock_out is None:
        # active session running
        return {
            "clocked_in": True,
            "status": "IN" if latest.session_type == "WORK" else "BREAK",
            "session": {
                "id": latest.id,
                "session_type": latest.session_type,
                "clock_in": latest.clock_in
            }
        }
        
    return {"clocked_in": False, "status": "OUT", "session": None}

@router.post("/clock-in", response_model=AttendanceResponse, summary="Clock In the start of a workday")
async def clock_in(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Attendance:
    employee = await get_active_employee(db, current_user.id)
    today = date.today()
    now = datetime.now(timezone.utc)
    
    att_repo = AttendanceRepository(db)
    record = await att_repo.get_day_record(employee.id, today)
    
    if not record:
        # Create a new daily attendance log
        # Determine status (PRESENT/REMOTE based on general headers or query defaults)
        record = Attendance(
            employee_id=employee.id,
            date=today,
            status="PRESENT",
            total_working_hours=0.0,
            overtime_minutes=0
        )
        record = await att_repo.create_attendance(record)
    else:
        # Verify if currently clocked in
        active_sessions = [s for s in record.sessions if s.clock_out is None]
        if active_sessions:
            raise ValidationException("Already clocked in or in an active session")
            
    # Add new session
    session = AttendanceSession(
        attendance_id=record.id,
        session_type="WORK",
        clock_in=now
    )
    db.add(session)
    await db.commit()
    await db.refresh(record)
    
    logger.info("employee_clocked_in", employee_id=str(employee.id))
    return record

@router.post("/break", response_model=AttendanceResponse, summary="Pause work and start break session")
async def start_break(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Attendance:
    employee = await get_active_employee(db, current_user.id)
    today = date.today()
    now = datetime.now(timezone.utc)
    
    att_repo = AttendanceRepository(db)
    record = await att_repo.get_day_record(employee.id, today)
    if not record:
        raise ValidationException("Not clocked in today yet")
        
    active_work = [s for s in record.sessions if s.clock_out is None and s.session_type == "WORK"]
    if not active_work:
        raise ValidationException("No active work session to pause")
        
    # Close work session
    work_sess = active_work[0]
    work_sess.clock_out = now
    
    # Create break session
    break_sess = AttendanceSession(
        attendance_id=record.id,
        session_type="BREAK",
        clock_in=now
    )
    db.add(break_sess)
    await db.commit()
    await db.refresh(record)
    
    logger.info("employee_started_break", employee_id=str(employee.id))
    return record

@router.post("/resume", response_model=AttendanceResponse, summary="Resume work session from break")
async def resume_work(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Attendance:
    employee = await get_active_employee(db, current_user.id)
    today = date.today()
    now = datetime.now(timezone.utc)
    
    att_repo = AttendanceRepository(db)
    record = await att_repo.get_day_record(employee.id, today)
    if not record:
        raise ValidationException("No attendance logs found for today")
        
    active_break = [s for s in record.sessions if s.clock_out is None and s.session_type == "BREAK"]
    if not active_break:
        raise ValidationException("Not in an active break session")
        
    # Close break session
    break_sess = active_break[0]
    break_sess.clock_out = now
    
    # Open work session
    work_sess = AttendanceSession(
        attendance_id=record.id,
        session_type="WORK",
        clock_in=now
    )
    db.add(work_sess)
    await db.commit()
    await db.refresh(record)
    
    logger.info("employee_resumed_work", employee_id=str(employee.id))
    return record

@router.post("/clock-out", response_model=AttendanceResponse, summary="Clock Out and terminate workday")
async def clock_out(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> Attendance:
    employee = await get_active_employee(db, current_user.id)
    today = date.today()
    now = datetime.now(timezone.utc)
    
    att_repo = AttendanceRepository(db)
    record = await att_repo.get_day_record(employee.id, today)
    if not record:
        raise ValidationException("No attendance logs found for today")
        
    active_sessions = [s for s in record.sessions if s.clock_out is None]
    if not active_sessions:
        raise ValidationException("Not clocked in")
        
    # Close active session
    active = active_sessions[0]
    active.clock_out = now
    
    # Calculate total working hours (sum of all WORK sessions durations in hours)
    # Refetch inside a refresh state to get all closed sessions
    await db.commit()
    await db.refresh(record)
    
    work_hours = 0.0
    for sess in record.sessions:
        if sess.session_type == "WORK" and sess.clock_out is not None:
            delta = sess.clock_out - sess.clock_in
            work_hours += delta.total_seconds() / 3600.0
            
    record.total_working_hours = round(work_hours, 2)
    
    # Overtime calculation: standard workday is 8 hours
    if work_hours > 8.0:
        overtime_min = int((work_hours - 8.0) * 60)
        record.overtime_minutes = overtime_min
        
    updated = await att_repo.update_attendance(record)
    logger.info("employee_clocked_out", employee_id=str(employee.id), hours=updated.total_working_hours)
    return updated

@router.get("/logs", response_model=List[AttendanceResponse], summary="Retrieve personal attendance logs")
async def get_my_logs(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[Attendance]:
    employee = await get_active_employee(db, current_user.id)
    att_repo = AttendanceRepository(db)
    return await att_repo.get_range_records(employee.id, start_date, end_date)
