import pytest
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4
from httpx import AsyncClient
from app.auth.security import hash_password
from app.models.user import User
from app.models.finance import Currency, FiscalYear, FiscalPeriod, CostCenter, GeneralLedgerAccount, CustomerInvoice, JournalEntry, JournalEntryLine
from app.models.crm import Customer, SalesOrder, SalesOrderItem
from app.models.inventory import Product
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_double_entry_balance_validation(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed accounts, cost centers, and open period
    fy = FiscalYear(name="FY-2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), status="OPEN")
    db_session.add(fy)
    await db_session.flush()

    fp = FiscalPeriod(fiscal_year_id=fy.id, name="Period-01", start_date=date(2026, 1, 1), end_date=date(2026, 1, 31), status="OPEN")
    db_session.add(fp)

    acc_cash = GeneralLedgerAccount(code="1000", name="Cash", account_type="ASSET")
    acc_revenue = GeneralLedgerAccount(code="4000", name="Revenue", account_type="REVENUE")
    db_session.add_all([acc_cash, acc_revenue])
    await db_session.commit()

    # Authenticate admin
    admin = User(
        email="testfinanceadmin@businessos.com",
        full_name="Finance Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Try posting unbalanced JE (Debits != Credits)
    payload = {
        "entry_date": "2026-01-15",
        "description": "Unbalanced entry testing",
        "lines": [
            {"account_id": str(acc_cash.id), "debit": 1000.0, "credit": 0.0},
            {"account_id": str(acc_revenue.id), "debit": 0.0, "credit": 800.0} # unbalanced by 200
        ]
    }
    response = await client.post("/api/v1/journal", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Unbalanced" in response.json()["detail"]

    # 3. Post balanced JE (Debits == Credits)
    payload_balanced = {
        "entry_date": "2026-01-15",
        "description": "Balanced entry testing",
        "lines": [
            {"account_id": str(acc_cash.id), "debit": 1000.0, "credit": 0.0},
            {"account_id": str(acc_revenue.id), "debit": 0.0, "credit": 1000.0}
        ]
    }
    balanced_res = await client.post("/api/v1/journal", json=payload_balanced, headers=headers)
    assert balanced_res.status_code == 201
    assert balanced_res.json()["status"] == "POSTED"
    assert balanced_res.json()["entry_number"].startswith("JE-2026-")

@pytest.mark.asyncio
async def test_posting_to_closed_period_blocked(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed closed fiscal period
    fy = FiscalYear(name="FY-2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), status="OPEN")
    db_session.add(fy)
    await db_session.flush()

    fp = FiscalPeriod(fiscal_year_id=fy.id, name="Period-02", start_date=date(2026, 2, 1), end_date=date(2026, 2, 28), status="CLOSED")
    db_session.add(fp)

    acc_cash = GeneralLedgerAccount(code="1000", name="Cash", account_type="ASSET")
    acc_revenue = GeneralLedgerAccount(code="4000", name="Revenue", account_type="REVENUE")
    db_session.add_all([acc_cash, acc_revenue])
    await db_session.commit()

    # Authenticate admin
    admin = User(
        email="testclosedadmin@businessos.com",
        full_name="Finance Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Try posting to closed period (Feb 2026)
    payload = {
        "entry_date": "2026-02-15",
        "description": "Closed period entry testing",
        "lines": [
            {"account_id": str(acc_cash.id), "debit": 100.0, "credit": 0.0},
            {"account_id": str(acc_revenue.id), "debit": 0.0, "credit": 100.0}
        ]
    }
    response = await client.post("/api/v1/journal", json=payload, headers=headers)
    assert response.status_code == 400
    assert "closed or locked period" in response.json()["detail"]
