import uuid
from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import AuditBase

class Department(AuditBase):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    head_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", use_alter=True, name="fk_dept_head"), nullable=True)
    budget: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    # Relationships
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department", foreign_keys="[Employee.department_id]")
    designations: Mapped[list["Designation"]] = relationship("Designation", back_populates="department")

class Designation(AuditBase):
    __tablename__ = "designations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hierarchy_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    salary_grade: Mapped[str] = mapped_column(String(50), nullable=True)

    # Relationships
    department: Mapped[Department] = relationship("Department", back_populates="designations")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="designation")

class Employee(AuditBase):
    __tablename__ = "employees"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    joining_date: Mapped[date] = mapped_column(Date, nullable=True)
    exit_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PROBATION", nullable=False) # ACTIVE, TERMINATED, ON_LEAVE, PROBATION
    employment_type: Mapped[str] = mapped_column(String(50), default="FULL_TIME", nullable=False) # FULL_TIME, PART_TIME, CONTRACT, INTERN
    onboarding_status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False) # DRAFT, OFFER_SENT, OFFER_ACCEPTED, DOCUMENTS_PENDING, DOCUMENTS_VERIFIED, IT_ACCOUNT_CREATED, ONBOARDING_COMPLETE

    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    designation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("designations.id"), nullable=True)
    manager_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id", name="fk_employee_manager"), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)

    emergency_contact_name: Mapped[str] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    emergency_contact_relation: Mapped[str] = mapped_column(String(100), nullable=True)
    tags: Mapped[str] = mapped_column(String(1024), nullable=True) # comma separated list of tags like "Leadership,Remote"

    # Relationships
    department: Mapped[Department] = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    designation: Mapped[Designation] = relationship("Designation", back_populates="employees")
    manager: Mapped["Employee"] = relationship("Employee", remote_side="[Employee.id]", back_populates="direct_reports")
    direct_reports: Mapped[list["Employee"]] = relationship("Employee", back_populates="manager")
    skills: Mapped[list["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    salary_history: Mapped[list["SalaryHistory"]] = relationship("SalaryHistory", back_populates="employee", cascade="all, delete-orphan")
    attendance: Mapped[list["Attendance"]] = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    leave_balances: Mapped[list["LeaveBalance"]] = relationship("LeaveBalance", back_populates="employee", cascade="all, delete-orphan")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee", foreign_keys="[LeaveRequest.employee_id]", cascade="all, delete-orphan")
    performance_reviews: Mapped[list["PerformanceReview"]] = relationship("PerformanceReview", back_populates="employee", foreign_keys="[PerformanceReview.employee_id]", cascade="all, delete-orphan")
    documents: Mapped[list["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")
    notes: Mapped[list["EmployeeNote"]] = relationship("EmployeeNote", back_populates="employee", cascade="all, delete-orphan")
    timeline: Mapped[list["EmployeeTimeline"]] = relationship("EmployeeTimeline", back_populates="employee", cascade="all, delete-orphan")

class EmployeeSkill(AuditBase):
    __tablename__ = "employee_skills"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    proficiency: Mapped[str] = mapped_column(String(50), default="INTERMEDIATE", nullable=False) # BEGINNER, INTERMEDIATE, EXPERT

    employee: Mapped[Employee] = relationship("Employee", back_populates="skills")

class SalaryHistory(AuditBase):
    __tablename__ = "salary_histories"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    base_salary: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    bonus: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    allowance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    deduction: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="salary_history")

class Attendance(AuditBase):
    __tablename__ = "attendance"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PRESENT", nullable=False) # PRESENT, ABSENT, HALF_DAY, REMOTE
    total_working_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overtime_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="attendance")
    sessions: Mapped[list["AttendanceSession"]] = relationship("AttendanceSession", back_populates="attendance", cascade="all, delete-orphan")

class AttendanceSession(AuditBase):
    __tablename__ = "attendance_sessions"

    attendance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("attendance.id"), nullable=False)
    session_type: Mapped[str] = mapped_column(String(50), default="WORK", nullable=False) # WORK, BREAK
    clock_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    clock_out: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    attendance: Mapped[Attendance] = relationship("Attendance", back_populates="sessions")

class LeaveType(AuditBase):
    __tablename__ = "leave_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    days_per_year: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

class LeaveBalance(AuditBase):
    __tablename__ = "leave_balances"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    leave_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    entitled: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    used: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pending: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="leave_balances")
    leave_type: Mapped[LeaveType] = relationship("LeaveType")

class LeaveRequest(AuditBase):
    __tablename__ = "leave_requests"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    leave_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING_MANAGER", nullable=False) # PENDING_MANAGER, PENDING_HR, APPROVED, REJECTED, CANCELLED
    approved_by_manager_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    approved_by_hr_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    rejection_reason: Mapped[str] = mapped_column(String(512), nullable=True)

    employee: Mapped[Employee] = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    leave_type: Mapped[LeaveType] = relationship("LeaveType")

class PerformanceReview(AuditBase):
    __tablename__ = "performance_reviews"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    review_cycle: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False) # 1-5 scale
    goals: Mapped[str] = mapped_column(String(2048), nullable=True)
    achievements: Mapped[str] = mapped_column(String(2048), nullable=True)
    strengths: Mapped[str] = mapped_column(String(2048), nullable=True)
    weaknesses: Mapped[str] = mapped_column(String(2048), nullable=True)
    manager_feedback: Mapped[str] = mapped_column(String(2048), nullable=True)
    self_review: Mapped[str] = mapped_column(String(2048), nullable=True)
    promotion_recommendation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="performance_reviews", foreign_keys=[employee_id])
    reviewer: Mapped[Employee] = relationship("Employee", foreign_keys=[reviewer_id])

class EmployeeDocument(AuditBase):
    __tablename__ = "employee_documents"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False) # Resume, Offer Letter, PAN, Aadhar, Passport, Contract, Certificate
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="documents")

class EmployeeNote(AuditBase):
    __tablename__ = "employee_notes"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), default="GENERAL", nullable=False) # PRIVATE_HR, MANAGER, GENERAL
    content: Mapped[str] = mapped_column(String(4096), nullable=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="notes")

class EmployeeTimeline(AuditBase):
    __tablename__ = "employee_timelines"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # JOINED, DEPT_CHANGED, PROMOTED, SALARY_UPDATED, LEAVE_APPROVED, PERFORMANCE_REVIEW, DOC_UPLOADED, ONBOARDING_STAGE
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

    employee: Mapped[Employee] = relationship("Employee", back_populates="timeline")
