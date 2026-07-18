import pytest
from httpx import AsyncClient
from app.auth.security import hash_password
from app.models.user import User
from app.models.analytics.kpis import KPIDefinition
from app.models.analytics.dashboard import Dashboard
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_semantic_metrics_calculations(client: AsyncClient, db_session: AsyncSession) -> None:
    # Authenticate admin
    admin = User(
        email="testanadmin@businessos.com",
        full_name="Analytics Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Query dynamic calculation via POST /api/v1/analytics/query
    query_payload = {
        "metric_code": "REVENUE",
        "dimensions": ["department"],
        "filters": {"date_range": "30d"}
    }
    res = await client.post("/api/v1/analytics/query", json=query_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["metric"] == "REVENUE"
    assert "value" in res.json()

@pytest.mark.asyncio
async def test_kpi_definitions_list(client: AsyncClient, db_session: AsyncSession) -> None:
    # Seed KPI
    kpi = KPIDefinition(
        name="Quarterly Revenue target",
        metric_code="REVENUE",
        target_value=100000.0,
        threshold_yellow=80000.0,
        threshold_red=50000.0,
        status="ACTIVE"
    )
    db_session.add(kpi)
    await db_session.commit()

    res = await client.get("/api/v1/analytics/kpis")
    assert res.status_code == 200
    assert len(res.json()) > 0
    assert res.json()[0]["metric_code"] == "REVENUE"

@pytest.mark.asyncio
async def test_dashboard_role_access(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed dashboard with CEO role restriction
    db_ceo = Dashboard(
        name="Top Executive dashboard",
        code="RESTRICTED_CEO_DASH",
        allowed_roles="CEO" # restricted to CEO role!
    )
    db_session.add(db_ceo)
    await db_session.commit()

    # 2. Authenticate EMPLOYEE user (unauthorized)
    employee = User(
        email="empuser@businessos.com",
        full_name="Employee User",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="EMPLOYEE",
    )
    db_session.add(employee)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": employee.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/api/v1/analytics/dashboards", headers=headers)
    assert res.status_code == 200
    # Restructed dashboard should be hidden/filtered out
    dashboard_codes = [d["code"] for d in res.json()]
    assert "RESTRICTED_CEO_DASH" not in dashboard_codes
