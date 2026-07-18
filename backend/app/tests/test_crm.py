import pytest
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4
from httpx import AsyncClient
from app.auth.security import hash_password
from app.models.user import User
from app.models.crm import Customer, Lead, Opportunity, PricingRule, SalesOrder, SalesOrderItem
from app.models.inventory import Warehouse, Product, Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest.mark.asyncio
async def test_lead_conversion_success(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed sales user
    sales = User(
        email="testcrmsales@businessos.com",
        full_name="Sales Executive",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="SALES",
    )
    db_session.add(sales)
    await db_session.commit()

    # Authenticate
    login_res = await client.post("/api/v1/auth/login", json={"email": sales.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Lead
    lead = Lead(
        first_name="Bruce",
        last_name="Wayne",
        company_name="Wayne Enterprises",
        email="bruce@waynecorp.com",
        phone="+15551234",
        source="MANUAL",
        status="NEW"
    )
    db_session.add(lead)
    await db_session.commit()

    # 3. Call conversion route
    response = await client.post(f"/api/v1/leads/{lead.id}/convert", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Wayne Enterprises"
    
    # Check lead status converted
    lead_res = await db_session.execute(select(Lead).where(Lead.id == lead.id))
    refetched = lead_res.scalar_one()
    assert refetched.status == "CONVERTED"
    assert refetched.converted_customer_id is not None

@pytest.mark.asyncio
async def test_pricing_engine_discount_rules(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Seed products, customer and VIP pricing rule
    prod = Product(
        sku="PRICING-TEST-PROD",
        name="Premium Laptop Workstation",
        cost_price=1000.0,
        selling_price=1500.0,
        tax_rate=0.0
    )
    db_session.add(prod)
    await db_session.flush()

    cust = Customer(
        name="VIP Customer Inc",
        customer_type="COMPANY",
        segment="VIP",
        status="ACTIVE"
    )
    db_session.add(cust)
    await db_session.flush()

    rule = PricingRule(
        name="VIP 20% Discount Rule",
        customer_segment="VIP",
        product_id=prod.id,
        discount_percentage=20.0, # 20% discount
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=5),
        priority=1
    )
    db_session.add(rule)
    await db_session.commit()

    # Authenticate admin
    admin = User(
        email="testpricingadmin@businessos.com",
        full_name="Pricing Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Call quotation endpoint and check if Pricing Engine applied VIP 20% discount (1500 * 0.8 = 1200)
    payload = {
        "customer_id": str(cust.id),
        "items": [{
            "product_id": str(prod.id),
            "quantity": 10.0,
            "unit_price": 1500.0
        }],
        "valid_until": str(date.today() + timedelta(days=10))
    }
    response = await client.post("/api/v1/quotations", json=payload, headers=headers)
    assert response.status_code == 201
    
    # 1200 * 10 = 12000.0 subtotal. total cost includes 18% default tax rate = 12000 * 1.18 = 14160
    assert response.json()["subtotal"] == 12000.0
    assert response.json()["total_amount"] == 14160.0

@pytest.mark.asyncio
async def test_sales_order_approval_stock_reservation(client: AsyncClient, db_session: AsyncSession) -> None:
    # 1. Create a product, warehouse, inventory levels
    prod = Product(
        sku="ORDER-STOCK-PROD",
        name="Standard Office Chair",
        cost_price=50.0,
        selling_price=100.0,
        tax_rate=0.0
    )
    db_session.add(prod)
    await db_session.flush()

    wh = Warehouse(
        name="Central Warehouse",
        code="WH-CENTRAL",
        capacity=1000.0
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
    await db_session.flush()

    cust = Customer(
        name="Retail Client",
        customer_type="COMPANY",
        status="ACTIVE"
    )
    db_session.add(cust)
    await db_session.flush()

    # 2. Add an Admin User for authentication
    admin = User(
        email="testorderadmin@businessos.com",
        full_name="Order Admin",
        password_hash=hash_password("SuperSecurePassword123!"),
        role="ADMIN",
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": "SuperSecurePassword123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Draft Sales Order
    so_payload = {
        "customer_id": str(cust.id),
        "items": [{
            "product_id": str(prod.id),
            "quantity": 10.0,
            "unit_price": 100.0
        }]
    }
    so_res = await client.post("/api/v1/orders", json=so_payload, headers=headers)
    assert so_res.status_code == 201
    so_id = so_res.json()["id"]

    # 4. Submit order
    submit_res = await client.post(f"/api/v1/orders/{so_id}/submit", headers=headers)
    assert submit_res.status_code == 200

    # 5. Approve order (Triggers Inventory Stock Reservation!)
    approve_res = await client.post(
        f"/api/v1/orders/{so_id}/approve",
        json={"approved": True, "comments": "Approve transaction"},
        headers=headers
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # 6. Verify inventory stock reserved
    inv_q = select(Inventory).where(Inventory.id == inv.id)
    inv_res = await db_session.execute(inv_q)
    refetched_inv = inv_res.scalar_one()
    assert refetched_inv.quantity_on_hand == 100.0
    assert refetched_inv.quantity_reserved == 10.0
    assert refetched_inv.quantity_available == 90.0
