import asyncio
from datetime import date, datetime, timezone
from app.auth.security import hash_password
from app.database.session import async_session_maker
from app.logging.config import logger
from app.models.user import User
from app.models.hcm import (
    Department,
    Designation,
    Employee,
    EmployeeSkill,
    SalaryHistory,
    LeaveType,
    LeaveBalance,
    EmployeeTimeline,
)
from sqlalchemy import select

async def seed_database() -> None:
    logger.info("starting_database_seeding")
    async with async_session_maker() as session:
        # Check if user database is already seeded
        query = select(User)
        result = await session.execute(query)
        first_user = result.scalars().first()
        
        # We will delete and re-seed or skip if already seeded
        if first_user is not None:
            logger.info("database_already_seeded_skipping")
            return

        # Users corresponding to distinct system roles
        users_to_seed = [
            ("superadmin@businessos.com", "Super Admin User", "SUPER_ADMIN"),
            ("admin@businessos.com", "Admin User", "ADMIN"),
            ("manager@businessos.com", "Manager User", "MANAGER"),
            ("hr@businessos.com", "HR User", "HR"),
            ("finance@businessos.com", "Finance User", "FINANCE"),
            ("sales@businessos.com", "Sales User", "SALES"),
            ("employee@businessos.com", "Employee User", "EMPLOYEE"),
        ]

        default_seed_password = "SuperSecurePassword123!"
        hashed_password = hash_password(default_seed_password)

        created_users = {}
        for email, full_name, role in users_to_seed:
            user = User(
                email=email,
                full_name=full_name,
                password_hash=hashed_password,
                role=role,
                phone="+15555550199",
                company_name="AI BusinessOS Ltd",
                profile_image=f"https://api.dicebear.com/7.x/initials/svg?seed={role}",
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            created_users[role] = user
            logger.info("queueing_seed_user", email=email, role=role)

        await session.flush()  # Generate User IDs without committing yet

        # 1. Seed Departments
        dept_engineering = Department(name="Engineering", description="Software and infrastructure systems", budget=1000000.0)
        dept_hr = Department(name="Human Resources", description="Talent management and acquisition", budget=200000.0)
        dept_sales = Department(name="Sales", description="Business growth and customer acquisition", budget=500000.0)
        session.add_all([dept_engineering, dept_hr, dept_sales])
        await session.flush()

        # 2. Seed Designations
        des_mgr = Designation(name="Engineering Manager", hierarchy_level=3, department_id=dept_engineering.id, salary_grade="E3")
        des_dev = Designation(name="Senior Developer", hierarchy_level=2, department_id=dept_engineering.id, salary_grade="E2")
        des_hr_lead = Designation(name="HR Manager", hierarchy_level=3, department_id=dept_hr.id, salary_grade="H3")
        des_rep = Designation(name="Sales Representative", hierarchy_level=1, department_id=dept_sales.id, salary_grade="S1")
        session.add_all([des_mgr, des_dev, des_hr_lead, des_rep])
        await session.flush()

        # 3. Seed Leave Types
        lt_annual = LeaveType(name="Annual Leave", code="AL", description="Yearly vacation leaves", days_per_year=20)
        lt_sick = LeaveType(name="Sick Leave", code="SL", description="Medical emergency leaves", days_per_year=10)
        lt_casual = LeaveType(name="Casual Leave", code="CL", description="Short personal leaves", days_per_year=7)
        session.add_all([lt_annual, lt_sick, lt_casual])
        await session.flush()

        # 4. Seed Employee profiles
        # Seed Manager Employee Profile
        emp_manager = Employee(
            user_id=created_users["MANAGER"].id,
            employee_id="EMP-0001",
            first_name="Marcus",
            last_name="Aurelius",
            email="manager@businessos.com",
            phone="+15555550001",
            joining_date=date(2025, 1, 1),
            status="ACTIVE",
            employment_type="FULL_TIME",
            onboarding_status="ONBOARDING_COMPLETE",
            department_id=dept_engineering.id,
            designation_id=des_mgr.id,
            location="Remote",
            tags="Leadership,Manager,Core",
        )
        session.add(emp_manager)
        await session.flush()

        # Set Department head
        dept_engineering.head_id = emp_manager.id

        # Seed Employee Profile reporting to Manager
        emp_dev = Employee(
            user_id=created_users["EMPLOYEE"].id,
            employee_id="EMP-0002",
            first_name="Dev",
            last_name="Developer",
            email="employee@businessos.com",
            phone="+15555550002",
            joining_date=date(2025, 6, 1),
            status="ACTIVE",
            employment_type="FULL_TIME",
            onboarding_status="ONBOARDING_COMPLETE",
            department_id=dept_engineering.id,
            designation_id=des_dev.id,
            manager_id=emp_manager.id,
            location="Remote",
            tags="Python,Developer,React",
        )
        session.add(emp_dev)

        # Seed HR Lead profile
        emp_hr = Employee(
            user_id=created_users["HR"].id,
            employee_id="EMP-0003",
            first_name="Harriett",
            last_name="Resources",
            email="hr@businessos.com",
            phone="+15555550003",
            joining_date=date(2025, 2, 1),
            status="ACTIVE",
            employment_type="FULL_TIME",
            onboarding_status="ONBOARDING_COMPLETE",
            department_id=dept_hr.id,
            designation_id=des_hr_lead.id,
            location="New York",
            tags="HR,Recruiting",
        )
        session.add(emp_hr)
        dept_hr.head_id = emp_hr.id

        # Seed onboarding status candidates (drafts, offer sent)
        emp_onboard1 = Employee(
            first_name="Alice",
            last_name="Wonderland",
            email="alice@wonderland.com",
            phone="+15555559999",
            status="PROBATION",
            employment_type="CONTRACT",
            onboarding_status="OFFER_SENT",
            department_id=dept_engineering.id,
            designation_id=des_dev.id,
            location="Remote",
        )
        emp_onboard2 = Employee(
            first_name="Bob",
            last_name="Builder",
            email="bob@builder.com",
            phone="+15555558888",
            status="PROBATION",
            employment_type="FULL_TIME",
            onboarding_status="DOCUMENTS_PENDING",
            department_id=dept_engineering.id,
            designation_id=des_dev.id,
            location="London",
        )
        session.add_all([emp_onboard1, emp_onboard2])
        await session.flush()

        # 5. Seed Skills
        skill_python = EmployeeSkill(employee_id=emp_dev.id, skill_name="Python", proficiency="EXPERT")
        skill_react = EmployeeSkill(employee_id=emp_dev.id, skill_name="React", proficiency="INTERMEDIATE")
        skill_docker = EmployeeSkill(employee_id=emp_dev.id, skill_name="Docker", proficiency="BEGINNER")
        session.add_all([skill_python, skill_react, skill_docker])

        # 6. Seed Salary History records
        salary_mgr = SalaryHistory(
            employee_id=emp_manager.id,
            effective_date=date(2025, 1, 1),
            base_salary=120000.0,
            bonus=10000.0,
            allowance=5000.0,
            reason="Starting appointment compensation structure",
            created_by_id=created_users["SUPER_ADMIN"].id,
        )
        salary_dev = SalaryHistory(
            employee_id=emp_dev.id,
            effective_date=date(2025, 6, 1),
            base_salary=85000.0,
            allowance=2000.0,
            reason="Starting appointment compensation structure",
            created_by_id=created_users["SUPER_ADMIN"].id,
        )
        session.add_all([salary_mgr, salary_dev])

        # 7. Seed Leave Balances
        for emp in (emp_manager, emp_dev, emp_hr):
            session.add_all([
                LeaveBalance(employee_id=emp.id, leave_type_id=lt_annual.id, entitled=20.0, year=2026),
                LeaveBalance(employee_id=emp.id, leave_type_id=lt_sick.id, entitled=10.0, year=2026),
                LeaveBalance(employee_id=emp.id, leave_type_id=lt_casual.id, entitled=7.0, year=2026),
            ])

        # 8. Seed Timelines
        timeline_mgr = EmployeeTimeline(
            employee_id=emp_manager.id,
            event_type="JOINED",
            event_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            title="Joined AI BusinessOS",
            description="Marcus Aurelius hired as Engineering Manager",
        )
        timeline_dev = EmployeeTimeline(
            employee_id=emp_dev.id,
            event_type="JOINED",
            event_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
            title="Joined AI BusinessOS",
            description="Dev Developer hired as Senior Software Engineer",
        )
        session.add_all([timeline_mgr, timeline_dev])

        await session.commit()
        logger.info("database_seeding_completed_successfully")

if __name__ == "__main__":
    asyncio.run(seed_database())
