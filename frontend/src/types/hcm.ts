export type OnboardingStatus =
  | 'DRAFT'
  | 'OFFER_SENT'
  | 'OFFER_ACCEPTED'
  | 'DOCUMENTS_PENDING'
  | 'DOCUMENTS_VERIFIED'
  | 'IT_ACCOUNT_CREATED'
  | 'ONBOARDING_COMPLETE';

export type EmployeeStatus = 'ACTIVE' | 'TERMINATED' | 'ON_LEAVE' | 'PROBATION';

export type EmploymentType = 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERN';

export type NoteType = 'PRIVATE_HR' | 'MANAGER' | 'GENERAL';

export interface Department {
  id: string;
  name: string;
  description?: string;
  head_id?: string;
  budget: number;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
}

export interface Designation {
  id: string;
  name: string;
  hierarchy_level: number;
  department_id?: string;
  salary_grade?: string;
}

export interface EmployeeSkill {
  id: string;
  employee_id: string;
  skill_name: string;
  proficiency: 'BEGINNER' | 'INTERMEDIATE' | 'EXPERT';
}

export interface SalaryHistory {
  id: string;
  employee_id: string;
  effective_date: string;
  base_salary: number;
  bonus: number;
  allowance: number;
  deduction: number;
  reason?: string;
  created_by_id: string;
  created_at: string;
}

export interface Employee {
  id: string;
  user_id?: string;
  employee_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  joining_date?: string;
  exit_date?: string;
  status: EmployeeStatus;
  employment_type: EmploymentType;
  onboarding_status: OnboardingStatus;
  department_id?: string;
  designation_id?: string;
  manager_id?: string;
  location?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  tags?: string;
  created_at: string;
  updated_at: string;
  
  skills?: EmployeeSkill[];
  department?: Department;
  designation?: Designation;
}

export interface AttendanceSession {
  id: string;
  attendance_id: string;
  session_type: 'WORK' | 'BREAK';
  clock_in: string;
  clock_out?: string;
}

export interface Attendance {
  id: string;
  employee_id: string;
  date: string;
  status: 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'REMOTE';
  total_working_hours: number;
  overtime_minutes: number;
  sessions: AttendanceSession[];
}

export interface LeaveType {
  id: string;
  name: string;
  code: string;
  description?: string;
  days_per_year: number;
}

export interface LeaveBalance {
  id: string;
  employee_id: string;
  leave_type_id: string;
  entitled: number;
  used: number;
  pending: number;
  year: number;
  leave_type?: LeaveType;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  leave_type_id: string;
  start_date: string;
  end_date: string;
  reason?: string;
  status: 'PENDING_MANAGER' | 'PENDING_HR' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  rejection_reason?: string;
  approved_by_manager_id?: string;
  approved_by_hr_id?: string;
  created_at: string;
  leave_type?: LeaveType;
  employee?: Employee;
}

export interface PerformanceReview {
  id: string;
  employee_id: string;
  reviewer_id: string;
  review_cycle: string;
  rating: number;
  goals?: string;
  achievements?: string;
  strengths?: string;
  weaknesses?: string;
  manager_feedback?: string;
  self_review?: string;
  promotion_recommendation: boolean;
  created_at: string;
}

export interface EmployeeDocument {
  id: string;
  employee_id: string;
  name: string;
  document_type: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  version: number;
  created_at: string;
}

export interface EmployeeNote {
  id: string;
  employee_id: string;
  author_id: string;
  note_type: NoteType;
  content: string;
  created_at: string;
}

export interface EmployeeTimeline {
  id: string;
  employee_id: string;
  event_type: string;
  event_date: string;
  title: string;
  description?: string;
}
