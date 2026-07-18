from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- DEPARTMENT SCHEMAS ---
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    budget: float = 0.0
    status: str = "ACTIVE"

class DepartmentCreate(DepartmentBase):
    head_id: Optional[UUID] = None

class DepartmentResponse(DepartmentBase):
    id: UUID
    head_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- DESIGNATION SCHEMAS ---
class DesignationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    hierarchy_level: int = 1
    salary_grade: Optional[str] = None

class DesignationCreate(DesignationBase):
    department_id: Optional[UUID] = None

class DesignationResponse(DesignationBase):
    id: UUID
    department_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- EMPLOYEE SKILL SCHEMAS ---
class EmployeeSkillBase(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=100)
    proficiency: str = "INTERMEDIATE" # BEGINNER, INTERMEDIATE, EXPERT

class EmployeeSkillResponse(EmployeeSkillBase):
    id: UUID
    employee_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

# --- SALARY HISTORY SCHEMAS ---
class SalaryHistoryBase(BaseModel):
    effective_date: date
    base_salary: float
    bonus: float = 0.0
    allowance: float = 0.0
    deduction: float = 0.0
    reason: Optional[str] = None

class SalaryHistoryCreate(SalaryHistoryBase):
    pass

class SalaryHistoryResponse(SalaryHistoryBase):
    id: UUID
    employee_id: UUID
    created_by_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- EMPLOYEE SCHEMAS ---
class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    joining_date: Optional[date] = None
    exit_date: Optional[date] = None
    status: str = "PROBATION"
    employment_type: str = "FULL_TIME"
    location: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    tags: Optional[str] = None # comma separated tags

class EmployeeCreate(EmployeeBase):
    user_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    base_salary: Optional[float] = None # Initial salary history

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    employment_type: Optional[str] = None
    onboarding_status: Optional[str] = None
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    location: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    tags: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: UUID
    employee_id: Optional[str] = None
    onboarding_status: str
    user_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    skills: List[EmployeeSkillResponse] = []
    department: Optional[DepartmentResponse] = None
    designation: Optional[DesignationResponse] = None

    model_config = ConfigDict(from_attributes=True)

# --- ATTENDANCE SCHEMAS ---
class AttendanceSessionBase(BaseModel):
    session_type: str = "WORK" # WORK, BREAK
    clock_in: datetime
    clock_out: Optional[datetime] = None

class AttendanceSessionResponse(AttendanceSessionBase):
    id: UUID
    attendance_id: UUID

    model_config = ConfigDict(from_attributes=True)

class AttendanceBase(BaseModel):
    date: date
    status: str = "PRESENT"
    total_working_hours: float = 0.0
    overtime_minutes: int = 0

class AttendanceResponse(AttendanceBase):
    id: UUID
    employee_id: UUID
    sessions: List[AttendanceSessionResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- LEAVE SCHEMAS ---
class LeaveTypeResponse(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str] = None
    days_per_year: int

    model_config = ConfigDict(from_attributes=True)

class LeaveBalanceResponse(BaseModel):
    id: UUID
    employee_id: UUID
    leave_type_id: UUID
    entitled: float
    used: float
    pending: float
    year: int
    leave_type: Optional[LeaveTypeResponse] = None

    model_config = ConfigDict(from_attributes=True)

class LeaveRequestCreate(BaseModel):
    leave_type_id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveRequestResponse(BaseModel):
    id: UUID
    employee_id: UUID
    leave_type_id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    approved_by_manager_id: Optional[UUID] = None
    approved_by_hr_id: Optional[UUID] = None
    created_at: datetime
    leave_type: Optional[LeaveTypeResponse] = None
    employee: Optional[EmployeeResponse] = None

    model_config = ConfigDict(from_attributes=True)

class LeaveRequestApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None

# --- PERFORMANCE SCHEMAS ---
class PerformanceReviewCreate(BaseModel):
    reviewer_id: UUID
    review_cycle: str
    rating: int = Field(..., ge=1, le=5)
    goals: Optional[str] = None
    achievements: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    manager_feedback: Optional[str] = None
    self_review: Optional[str] = None
    promotion_recommendation: bool = False

class PerformanceReviewResponse(PerformanceReviewCreate):
    id: UUID
    employee_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- DOCUMENT SCHEMAS ---
class EmployeeDocumentResponse(BaseModel):
    id: UUID
    employee_id: UUID
    name: str
    document_type: str
    file_path: str
    file_size: int
    mime_type: str
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- NOTE SCHEMAS ---
class EmployeeNoteCreate(BaseModel):
    note_type: str = "GENERAL" # PRIVATE_HR, MANAGER, GENERAL
    content: str = Field(..., min_length=1)

class EmployeeNoteResponse(EmployeeNoteCreate):
    id: UUID
    employee_id: UUID
    author_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- TIMELINE SCHEMAS ---
class EmployeeTimelineResponse(BaseModel):
    id: UUID
    employee_id: UUID
    event_type: str
    event_date: datetime
    title: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
