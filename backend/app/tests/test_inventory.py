import pytest
from datetime import date
from uuid import uuid4
from httpx import AsyncClient
from app.auth.security import hash_password
from app.models.user import User
from app.models.inventory import Warehouse, Product, Inventory, ReorderRule, PurchaseOrder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_warehouse_success(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed admin
    admin = User(
        email="testwhadmin@businessos.com",
        full_name="Warehouse Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    # Authenticate
    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Midwest Distribution Center",
        "code": "WH-MIDWEST",
        "address": "400 Logistic Lane, Chicago, IL",
        "capacity": 3000.0,
        "status": "ACTIVE"
    }
    response = await client.post("/api/v1/warehouses", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == payload["name"]
    assert response.json()["code"] == payload["code"]

@pytest.mark.asyncio
async def test_stock_reservations_logic(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Create a product and inventory level
    prod = Product(
        sku="TEST-SKU-01",
        name="Test Item Pro",
        cost_price=10.0,
        selling_price=15.0,
        tax_rate=0.0
    )
    db_session.add(prod)
    await db_session.flush()

    wh = Warehouse(
        name="Test Reserve Wh",
        code="WH-TEST-RES",
        capacity=500.0
    )
    db_session.add(wh)
    await db_session.flush()

    inv = Inventory(
        warehouse_id=wh.id,
        product_id=prod.id,
        quantity_on_hand=100.0,
        quantity_reserved=0.0,
        quantity_available=100.0,
        quantity_incoming=0.0
    )
    db_session.add(inv)
    await db_session.commit()

    # 2. Add an Admin User for headers
    admin = User(
        email="testresadmin@businessos.com",
        full_name="Reserve Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Simulate PO / Stock allocation and perform reservation check
    # Check that available stock decreases
    from app.repositories.inventory_repository import InventoryRepository
    repo = InventoryRepository(db_session)
    success = await repo.reserve_stock(
        warehouse_id=wh.id,
        product_id=prod.id,
        quantity=30.0,
        reference_type="SALES_ORDER",
        reference_id=uuid4()
    )
    assert success is True

    # Refetch
    inv_res = await db_session.execute(select(Inventory).where(Inventory.id == inv.id))
    refetched = inv_res.scalar_one()
    assert refetched.quantity_on_hand == 100.0
    assert refetched.quantity_reserved == 30.0
    assert refetched.quantity_available == 70.0

@pytest.mark.asyncio
async def test_reorder_low_stock_rules(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Create a product and low inventory level
    prod = Product(
        sku="TEST-SKU-LOW",
        name="Test Low Stock Item",
        cost_price=5.0,
        selling_price=10.0,
        tax_rate=0.0
    )
    db_session.add(prod)
    await db_session.flush()

    wh = Warehouse(
        name="Test Low Wh",
        code="WH-TEST-LOW",
        capacity=500.0
    )
    db_session.add(wh)
    await db_session.flush()

    inv = Inventory(
        warehouse_id=wh.id,
        product_id=prod.id,
        quantity_on_hand=5.0, # Below min stock of 10
        quantity_reserved=0.0,
        quantity_available=5.0,
        quantity_incoming=0.0
    )
    db_session.add(inv)

    rule = ReorderRule(
        warehouse_id=wh.id,
        product_id=prod.id,
        min_stock=10.0,
        max_stock=100.0,
        safety_stock=2.0,
        reorder_quantity=50.0
    )
    db_session.add(rule)
    await db_session.commit()

    # 2. Add an Admin User for authentication
    admin = User(
        email="testlowadmin@businessos.com",
        full_name="Low Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch alerts
    response = await client.get("/api/v1/inventory/low-stock", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["product"] == "Test Low Stock Item"
    assert response.json()[0]["available"] == 5.0
