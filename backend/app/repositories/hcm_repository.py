from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.hcm import (
    Attendance,
    AttendanceSession,
    Department,
    Designation,
    Employee,
    EmployeeDocument,
    EmployeeNote,
    EmployeeSkill,
    EmployeeTimeline,
    LeaveBalance,
    LeaveRequest,
    LeaveType,
    PerformanceReview,
    SalaryHistory,
)

class EmployeeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, employee_id: UUID, include_deleted: bool = False) -> Optional[Employee]:
        query = select(Employee).where(Employee.id == employee_id)
        if not include_deleted:
            query = query.where(Employee.deleted_at.is_(None))
        query = query.options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.skills),
            selectinload(Employee.manager),
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[Employee]:
        query = select(Employee).where(Employee.email == email)
        if not include_deleted:
            query = query.where(Employee.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_user_id(self, user_id: UUID) -> Optional[Employee]:
        query = select(Employee).where(
            and_(Employee.user_id == user_id, Employee.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all_paginated(
        self,
        search: Optional[str] = None,
        department_id: Optional[UUID] = None,
        designation_id: Optional[UUID] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        manager_id: Optional[UUID] = None,
        employment_type: Optional[str] = None,
        tag: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "last_name",
        sort_order: str = "asc",
    ) -> tuple[List[Employee], int]:
        # Filter out soft deleted records
        query = select(Employee).where(Employee.deleted_at.is_(None))

        # Filter criteria
        if department_id:
            query = query.where(Employee.department_id == department_id)
        if designation_id:
            query = query.where(Employee.designation_id == designation_id)
        if status:
            query = query.where(Employee.status == status)
        if location:
            query = query.where(Employee.location == location)
        if manager_id:
            query = query.where(Employee.manager_id == manager_id)
        if employment_type:
            query = query.where(Employee.employment_type == employment_type)
        if tag:
            query = query.where(Employee.tags.like(f"%{tag}%"))

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Employee.first_name.like(search_pattern))
                | (Employee.last_name.like(search_pattern))
                | (Employee.email.like(search_pattern))
                | (Employee.employee_id.like(search_pattern))
            )

        # Count total matches before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar_one()

        # Sorting logic
        sort_column = getattr(Employee, sort_by, Employee.last_name)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Pagination
        query = query.offset(skip).limit(limit).options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total_count

    async def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def update(self, employee: Employee) -> Employee:
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def soft_delete(self, employee: Employee) -> Employee:
        employee.soft_delete()
        await self.db.commit()
        return employee

    async def restore(self, employee: Employee) -> Employee:
        employee.restore()
        await self.db.commit()
        return employee


class DepartmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, dept_id: UUID) -> Optional[Department]:
        query = select(Department).where(and_(Department.id == dept_id, Department.deleted_at.is_(None)))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[Department]:
        query = select(Department).where(Department.deleted_at.is_(None))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_headcount_stats(self) -> List[dict]:
        # Simple aggregates counting active employees per department
        query = (
            select(Department.id, Department.name, func.count(Employee.id))
            .join(Employee, Employee.department_id == Department.id)
            .where(and_(Employee.deleted_at.is_(None), Employee.status == "ACTIVE"))
            .group_by(Department.id, Department.name)
        )
        result = await self.db.execute(query)
        return [{"id": r[0], "name": r[1], "count": r[2]} for r in result.all()]

    async def create(self, dept: Department) -> Department:
        self.db.add(dept)
        await self.db.commit()
        await self.db.refresh(dept)
        return dept

    async def update(self, dept: Department) -> Department:
        await self.db.commit()
        await self.db.refresh(dept)
        return dept


class DesignationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, des_id: UUID) -> Optional[Designation]:
        query = select(Designation).where(and_(Designation.id == des_id, Designation.deleted_at.is_(None)))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[Designation]:
        query = select(Designation).where(Designation.deleted_at.is_(None))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, des: Designation) -> Designation:
        self.db.add(des)
        await self.db.commit()
        await self.db.refresh(des)
        return des


class AttendanceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_day_record(self, employee_id: UUID, day: date) -> Optional[Attendance]:
        query = (
            select(Attendance)
            .where(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date == day,
                    Attendance.deleted_at.is_(None),
                )
            )
            .options(selectinload(Attendance.sessions))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_attendance(self, att: Attendance) -> Attendance:
        self.db.add(att)
        await self.db.commit()
        await self.db.refresh(att)
        return att

    async def update_attendance(self, att: Attendance) -> Attendance:
        await self.db.commit()
        await self.db.refresh(att)
        return att

    async def get_range_records(self, employee_id: UUID, start: date, end: date) -> List[Attendance]:
        query = (
            select(Attendance)
            .where(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date >= start,
                    Attendance.date <= end,
                    Attendance.deleted_at.is_(None),
                )
            )
            .options(selectinload(Attendance.sessions))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class LeaveRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_balances(self, employee_id: UUID, year: int) -> List[LeaveBalance]:
        query = (
            select(LeaveBalance)
            .where(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.year == year,
                    LeaveBalance.deleted_at.is_(None),
                )
            )
            .options(selectinload(LeaveBalance.leave_type))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_request(self, req: LeaveRequest) -> LeaveRequest:
        self.db.add(req)
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def get_request_by_id(self, req_id: UUID) -> Optional[LeaveRequest]:
        query = select(LeaveRequest).where(
            and_(LeaveRequest.id == req_id, LeaveRequest.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all_requests_paginated(
        self,
        manager_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[LeaveRequest]:
        query = select(LeaveRequest).where(LeaveRequest.deleted_at.is_(None))

        if employee_id:
            query = query.where(LeaveRequest.employee_id == employee_id)
        if manager_id:
            # Query direct reports matching manager_id
            query = query.join(Employee, Employee.id == LeaveRequest.employee_id).where(
                Employee.manager_id == manager_id
            )
        if status:
            query = query.where(LeaveRequest.status == status)

        query = query.order_by(desc(LeaveRequest.created_at)).offset(skip).limit(limit).options(
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.leave_type),
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_request(self, req: LeaveRequest) -> LeaveRequest:
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def update_balance(self, balance: LeaveBalance) -> LeaveBalance:
        await self.db.commit()
        await self.db.refresh(balance)
        return balance


class SalaryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_history(self, employee_id: UUID) -> List[SalaryHistory]:
        query = (
            select(SalaryHistory)
            .where(
                and_(SalaryHistory.employee_id == employee_id, SalaryHistory.deleted_at.is_(None))
            )
            .order_by(desc(SalaryHistory.effective_date))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_history(self, history: SalaryHistory) -> SalaryHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history
