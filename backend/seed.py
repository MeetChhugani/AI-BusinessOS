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
from app.models.inventory import (
    Warehouse,
    WarehouseLocation,
    Supplier,
    ProductCategory,
    Unit,
    Product,
    ProductImage,
    ProductVariant,
    Inventory,
    InventoryTransaction,
    ReorderRule,
    ProductTimeline,
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

        # --- Phase 2: HCM SEEDS ---
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

        # Seed onboarding status candidates
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

        # Seed Skills
        skill_python = EmployeeSkill(employee_id=emp_dev.id, skill_name="Python", proficiency="EXPERT")
        skill_react = EmployeeSkill(employee_id=emp_dev.id, skill_name="React", proficiency="INTERMEDIATE")
        skill_docker = EmployeeSkill(employee_id=emp_dev.id, skill_name="Docker", proficiency="BEGINNER")
        session.add_all([skill_python, skill_react, skill_docker])

        # Seed Salary History records
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

        # Seed Leave Balances
        for emp in (emp_manager, emp_dev, emp_hr):
            session.add_all([
                LeaveBalance(employee_id=emp.id, leave_type_id=lt_annual.id, entitled=20.0, year=2026),
                LeaveBalance(employee_id=emp.id, leave_type_id=lt_sick.id, entitled=10.0, year=2026),
                LeaveBalance(employee_id=emp.id, leave_type_id=lt_casual.id, entitled=7.0, year=2026),
            ])

        # Seed Timelines
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

        # --- Phase 3: INVENTORY SEEDS ---
        # 1. Seed Warehouses
        wh_central = Warehouse(name="Central Warehouse", code="WH-CENTRAL", address="100 Logistics Blvd, NY", capacity=5000.0, status="ACTIVE", manager_id=emp_manager.id)
        wh_retail = Warehouse(name="NY Retail Hub", code="WH-NYRETAIL", address="50 Broadway, NY", capacity=1000.0, status="ACTIVE")
        session.add_all([wh_central, wh_retail])
        await session.flush()

        # 2. Seed Locations (Zone/Rack/Shelf/Bin)
        loc_a = WarehouseLocation(warehouse_id=wh_central.id, zone="A", rack="03", shelf="B", bin="12", code="WH1-ZA-R03-SB-B12")
        loc_b = WarehouseLocation(warehouse_id=wh_central.id, zone="B", rack="01", shelf="A", bin="01", code="WH1-ZB-R01-SA-B01")
        session.add_all([loc_a, loc_b])
        await session.flush()

        # 3. Seed Suppliers
        supplier_tech = Supplier(
            name="TechCorp Solutions",
            code="SUP-TECH",
            contact_name="Sarah Connor",
            email="sales@techcorp.com",
            phone="+1555100200",
            gst_number="27AAAAA1111A1Z1",
            address="Silicone Valley, CA",
            payment_terms="NET30",
            rating=4.8
        )
        supplier_office = Supplier(
            name="Globex Logistics",
            code="SUP-GLOBEX",
            contact_name="Homer Simpson",
            email="shipments@globex.com",
            phone="+1555200300",
            gst_number="27BBBBB2222B2Z2",
            address="Springfield, OR",
            payment_terms="NET60",
            rating=3.9,
            late_delivery_count=3,
            defect_rate=2.5,
            cancellation_rate=1.0
        )
        session.add_all([supplier_tech, supplier_office])
        await session.flush()

        # 4. Seed Product Categories
        cat_elec = ProductCategory(name="Electronics", code="CAT-ELEC", description="Smartphones, laptops, and components", status="ACTIVE")
        cat_office = ProductCategory(name="Office Supplies", code="CAT-OFFICE", description="Desks, stationary, and materials", status="ACTIVE")
        session.add_all([cat_elec, cat_office])
        await session.flush()

        # 5. Seed Units of Measurement
        unit_pcs = Unit(name="Piece", code="PCS")
        unit_box = Unit(name="Box", code="BOX")
        session.add_all([unit_pcs, unit_box])
        await session.flush()

        # 6. Seed Products
        prod_laptop = Product(
            sku="PROD-LAP-15",
            barcode="880949123456",
            qr_code="QR-LAP-15",
            name="Laptop Pro 15",
            description="High performance 15 inch engineering workstation",
            category_id=cat_elec.id,
            brand="Intellect",
            cost_price=1200.00,
            selling_price=1800.00,
            tax_rate=18.0,
            weight=2.1,
            dimensions="35x24x2 cm",
            unit_id=unit_pcs.id,
            status="ACTIVE"
        )
        prod_mouse = Product(
            sku="PROD-MSE-01",
            barcode="880949123457",
            qr_code="QR-MSE-01",
            name="Wireless Mouse Premium",
            description="Ergonomic Bluetooth office mouse",
            category_id=cat_elec.id,
            brand="Intellect",
            cost_price=35.00,
            selling_price=65.00,
            tax_rate=18.0,
            weight=0.15,
            dimensions="12x7x4 cm",
            unit_id=unit_pcs.id,
            status="ACTIVE"
        )
        session.add_all([prod_laptop, prod_mouse])
        await session.flush()

        # Seed Product Timelines
        session.add_all([
            ProductTimeline(product_id=prod_laptop.id, event_type="CREATED", description="Laptop Pro 15 product initialized"),
            ProductTimeline(product_id=prod_mouse.id, event_type="CREATED", description="Wireless Mouse Premium product initialized"),
        ])

        # 7. Seed Product Images
        img_laptop = ProductImage(product_id=prod_laptop.id, image_url="https://images.unsplash.com/photo-1496181130204-7552cc1524e2?w=500", is_primary=True)
        img_mouse = ProductImage(product_id=prod_mouse.id, image_url="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500", is_primary=True)
        session.add_all([img_laptop, img_mouse])
        await session.flush()

        # 8. Seed Product Variants
        var_laptop_red = ProductVariant(
            product_id=prod_laptop.id,
            sku="PROD-LAP-15-RED",
            barcode="880949123458",
            name="Laptop Pro 15 - Red Edition",
            cost_price=1250.00,
            selling_price=1850.00,
            attribute_values={"color": "Red"}
        )
        session.add(var_laptop_red)
        await session.flush()

        # 9. Seed Inventory levels
        inv_laptop = Inventory(
            warehouse_id=wh_central.id,
            location_id=loc_a.id,
            product_id=prod_laptop.id,
            quantity_on_hand=50.0,
            quantity_reserved=5.0,
            quantity_available=45.0,
            quantity_incoming=0.0
        )
        inv_mouse = Inventory(
            warehouse_id=wh_central.id,
            location_id=loc_b.id,
            product_id=prod_mouse.id,
            quantity_on_hand=200.0,
            quantity_reserved=20.0,
            quantity_available=180.0,
            quantity_incoming=50.0
        )
        session.add_all([inv_laptop, inv_mouse])
        await session.flush()

        # 10. Seed Inventory Transactions
        txn_laptop = InventoryTransaction(
            inventory_id=inv_laptop.id,
            transaction_type="INBOUND",
            quantity=50.0,
            reference_document="GRN-0001",
            cost_price=1200.00,
            user_id=created_users["SUPER_ADMIN"].id,
            notes="Initial seed stock load"
        )
        txn_mouse = InventoryTransaction(
            inventory_id=inv_mouse.id,
            transaction_type="INBOUND",
            quantity=200.0,
            reference_document="GRN-0002",
            cost_price=35.00,
            user_id=created_users["SUPER_ADMIN"].id,
            notes="Initial seed stock load"
        )
        session.add_all([txn_laptop, txn_mouse])

        # 11. Seed Reorder rules
        rule_laptop = ReorderRule(
            warehouse_id=wh_central.id,
            product_id=prod_laptop.id,
            min_stock=10.0,
            max_stock=100.0,
            safety_stock=5.0,
            reorder_quantity=50.0
        )
        session.add(rule_laptop)

        await session.commit()
        logger.info("database_seeding_completed_successfully")

if __name__ == "__main__":
    asyncio.run(seed_database())
