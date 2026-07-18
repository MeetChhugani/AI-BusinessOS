import pytest
from datetime import date
from uuid import uuid4
from httpx import AsyncClient
from app.auth.security import hash_password
from app.models.user import User
from app.models.hcm import Employee, Department, Designation, SalaryHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_department_success(client: AsyncClient, db_session: AsyncSession) -> None:
    # Authenticate as Admin
    admin = User(
        email="testadmin@businessos.com",
        full_name="Test Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Quality Assurance",
        "description": "Verification systems",
        "budget": 150000.0,
        "status": "ACTIVE"
    }
    response = await client.post("/api/v1/departments", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == payload["name"]

@pytest.mark.asyncio
async def test_salary_access_rbac(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Create Super Admin (creator)
    superadmin = User(
        email="sa@businessos.com",
        full_name="Super Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="SUPER_ADMIN",
    )
    db_session.add(superadmin)
    await db_session.commit()

    # 2. Create target Employee (Emp 1)
    emp_user = User(
        email="emp1@businessos.com",
        full_name="Emp One",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="EMPLOYEE",
    )
    db_session.add(emp_user)
    await db_session.flush()

    emp_profile = Employee(
        user_id=emp_user.id,
        employee_id="EMP-9001",
        first_name="Emp",
        last_name="One",
        email=emp_user.email,
        status="ACTIVE",
    )
    db_session.add(emp_profile)
    await db_session.flush()

    salary_rec = SalaryHistory(
        employee_id=emp_profile.id,
        effective_date=date.today(),
        base_salary=50000.0,
        created_by_id=superadmin.id
    )
    db_session.add(salary_rec)

    # 3. Create another employee (Emp 2) who is unauthorized to see Emp 1's salary
    emp_user_2 = User(
        email="emp2@businessos.com",
        full_name="Emp Two",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="EMPLOYEE",
    )
    db_session.add(emp_user_2)
    await db_session.flush()

    emp_profile_2 = Employee(
        user_id=emp_user_2.id,
        employee_id="EMP-9002",
        first_name="Emp",
        last_name="Two",
        email=emp_user_2.email,
        status="ACTIVE",
    )
    db_session.add(emp_profile_2)
    await db_session.commit()

    # Authenticate as Emp 2
    login_res = await client.post("/api/v1/auth/login", json={"email": emp_user_2.email, "password": "SuperSecurePassword123!"})
    token_emp2 = login_res.json()["access_token"]
    headers_emp2 = {"Authorization": f"Bearer {token_emp2}"}

    # Attempt to retrieve salary of Emp 1
    response = await client.get(f"/api/v1/employees/{emp_profile.id}/salary", headers=headers_emp2)
    assert response.status_code == 403

    # Authenticate as Emp 1
    login_res_1 = await client.post("/api/v1/auth/login", json={"email": emp_user.email, "password": "SuperSecurePassword123!"})
    token_emp1 = login_res_1.json()["access_token"]
    headers_emp1 = {"Authorization": f"Bearer {token_emp1}"}

    # Retrieve own salary
    response_self = await client.get(f"/api/v1/employees/{emp_profile.id}/salary", headers=headers_emp1)
    assert response_self.status_code == 200
    assert response_self.json()[0]["base_salary"] == 50000.0

@pytest.mark.asyncio
async def test_attendance_clocking(client: AsyncClient, db_session: AsyncSession) -> None:
    # Create employee user
    user = User(
        email="clock@businessos.com",
        full_name="Clock User",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="EMPLOYEE",
    )
    db_session.add(user)
    await db_session.flush()

    employee = Employee(
        user_id=user.id,
        employee_id="EMP-9005",
        first_name="Clock",
        last_name="User",
        email=user.email,
        status="ACTIVE",
    )
    db_session.add(employee)
    await db_session.commit()

    # Authenticate
    login_res = await client.post("/api/v1/auth/login", json={"email": user.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get status (should be OUT)
    status_res = await client.get("/api/v1/attendance/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["clocked_in"] is False

    # Clock In
    clock_in_res = await client.post("/api/v1/attendance/clock-in", headers=headers)
    assert clock_in_res.status_code == 200

    # Get status (should be IN)
    status_res = await client.get("/api/v1/attendance/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["clocked_in"] is True
    assert status_res.json()["status"] == "IN"

    # Toggle Break
    break_res = await client.post("/api/v1/attendance/break", headers=headers)
    assert break_res.status_code == 200

    # Get status (should be BREAK)
    status_res = await client.get("/api/v1/attendance/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "BREAK"

    # Resume Work
    resume_res = await client.post("/api/v1/attendance/resume", headers=headers)
    assert resume_res.status_code == 200

    # Clock Out
    clock_out_res = await client.post("/api/v1/attendance/clock-out", headers=headers)
    assert clock_out_res.status_code == 200
    assert clock_out_res.json()["total_working_hours"] >= 0.0
