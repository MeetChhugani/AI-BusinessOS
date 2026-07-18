import asyncio
from datetime import date, datetime, timezone, timedelta
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
from app.models.crm import (
    SalesTerritory,
    Customer,
    CustomerContact,
    CustomerAddress,
    CustomerNote,
    CustomerActivityLog,
    Lead,
    LeadActivity,
    Opportunity,
    OpportunityProduct,
    PricingRule,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
    CommunicationTemplate,
    CRMTask,
    CRMMeeting,
    CRMCommunication,
)
from app.models.finance import (
    Currency,
    FiscalYear,
    FiscalPeriod,
    CostCenter,
    GeneralLedgerAccount,
    TaxConfiguration,
    TaxRate,
    ExpenseCategory,
)
from sqlalchemy import select

async def seed_database() -> None:
    logger.info("starting_database_seeding")
    async with async_session_maker() as session:
        # Check if user database is already seeded
        query = select(User)
        result = await session.execute(query)
        first_user = result.scalars().first()
        
        # We will skip if already seeded
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

        # --- Phase 4: CRM SEEDS ---
        # 1. Seed Sales Territories
        st_north = SalesTerritory(name="North America Division", region="North", assigned_salesperson_id=created_users["SALES"].id)
        st_west = SalesTerritory(name="West Coast Hub", region="West", assigned_salesperson_id=created_users["SALES"].id)
        session.add_all([st_north, st_west])
        await session.flush()

        # 2. Seed Pricing Rules (Pricing Engine rules)
        rule_vip_elec = PricingRule(
            name="VIP Electronics Discount",
            customer_segment="VIP",
            product_id=prod_laptop.id,
            discount_percentage=15.0, # 15% discount
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=90),
            priority=10
        )
        session.add(rule_vip_elec)

        # 3. Seed Customers
        cust_acme = Customer(
            name="Acme Corporation",
            customer_type="COMPANY",
            gst_number="27ACMEE1111A1Z1",
            industry="Manufacturing",
            segment="VIP",
            credit_limit=500000.00,
            payment_terms="NET30",
            territory_id=st_north.id,
            status="ACTIVE"
        )
        cust_globex = Customer(
            name="Globex Corp Ltd",
            customer_type="COMPANY",
            gst_number="27GLOBX2222B2Z2",
            industry="Technology",
            segment="ENTERPRISE",
            credit_limit=1000000.00,
            payment_terms="NET45",
            territory_id=st_west.id,
            status="ACTIVE"
        )
        session.add_all([cust_acme, cust_globex])
        await session.flush()

        # Seed Customer Contacts
        contact_acme = CustomerContact(customer_id=cust_acme.id, first_name="Wile", last_name="Coyote", email="wcoyote@acme.com", phone="+1555900100", job_title="Procurement Director", is_primary=True)
        contact_globex = CustomerContact(customer_id=cust_globex.id, first_name="Hank", last_name="Scorpio", email="hscorpio@globex.com", phone="+1555900200", job_title="CEO", is_primary=True)
        session.add_all([contact_acme, contact_globex])

        # Seed Customer Addresses
        addr_acme = CustomerAddress(customer_id=cust_acme.id, address_type="BILLING", address_line1="123 Desert Road", city="Phoenix", state="AZ", country="US", zip_code="85001")
        addr_globex = CustomerAddress(customer_id=cust_globex.id, address_type="BILLING", address_line1="456 Cypress Way", city="Cypress Creek", state="OR", country="US", zip_code="97401")
        session.add_all([addr_acme, addr_globex])

        # Seed Activity Logs
        session.add_all([
            CustomerActivityLog(customer_id=cust_acme.id, activity_type="CALL", description="Called Wile to confirm laptop specs requirements", created_by_id=created_users["SALES"].id),
            CustomerActivityLog(customer_id=cust_globex.id, activity_type="MEETING", description="Initial discovery meeting with Hank Scorpio", created_by_id=created_users["SALES"].id),
        ])

        # 4. Seed Leads
        lead_wayne = Lead(
            first_name="Bruce",
            last_name="Wayne",
            company_name="Wayne Enterprises",
            email="bruce@waynecorp.com",
            phone="+1555800900",
            source="REFERRAL",
            status="NEW",
            score=0.0,
            assigned_to_id=created_users["SALES"].id
        )
        session.add(lead_wayne)
        await session.flush()

        # Seed Lead Activities
        session.add(LeadActivity(lead_id=lead_wayne.id, activity_type="NOTE", details="Met Bruce at charity gala. Expressed interest in bulk hardware upgrades.", created_by_id=created_users["SALES"].id))

        # 5. Seed Opportunities
        opp_acme = Opportunity(
            name="Acme Laptop Fleet Upgrade",
            customer_id=cust_acme.id,
            stage="QUALIFICATION",
            probability=20.0,
            expected_revenue=90000.00,
            close_date=date.today() + timedelta(days=30),
            risk_level="MEDIUM",
            assigned_to_id=created_users["SALES"].id
        )
        session.add(opp_acme)
        await session.flush()

        # Seed Opportunity products
        opp_prod = OpportunityProduct(
            opportunity_id=opp_acme.id,
            product_id=prod_laptop.id,
            quantity=50.0,
            unit_price=1800.00
        )
        session.add(opp_prod)

        # 6. Seed Tasks
        session.add(CRMTask(
            title="Follow up with Bruce Wayne",
            description="Send company catalog specs sheet",
            due_date=datetime.now(timezone.utc) + timedelta(days=2),
            priority="HIGH",
            status="PENDING",
            assigned_to_id=created_users["SALES"].id,
            lead_id=lead_wayne.id
        ))
        await session.flush()

        # --- Phase 5: FINANCE SEEDS ---
        # 1. Seed Currencies
        cur_usd = Currency(code="USD", name="US Dollar", symbol="$", is_base=True)
        cur_inr = Currency(code="INR", name="Indian Rupee", symbol="₹", is_base=False)
        session.add_all([cur_usd, cur_inr])
        await session.flush()

        # 2. Seed Fiscal Year and custom open periods (April to March)
        fy_2026 = FiscalYear(name="FY-2026", start_date=date(2026, 4, 1), end_date=date(2027, 3, 31), status="OPEN")
        session.add(fy_2026)
        await session.flush()

        # Generate months for fiscal periods
        for m in range(1, 13):
            # Calendar year shifts: April (1) -> Dec (9) in 2026, Jan (10) -> Mar (12) in 2027
            c_year = 2026 if m <= 9 else 2027
            c_month = (m + 3) if m <= 9 else (m - 9)
            p_start = date(c_year, c_month, 1)
            p_end = date(c_year, c_month, 28) # simpler approximation
            fp = FiscalPeriod(
                fiscal_year_id=fy_2026.id,
                name=f"Period-{m:02d}",
                start_date=p_start,
                end_date=p_end,
                status="OPEN"
            )
            session.add(fp)

        # 3. Seed Cost Centers
        cc_eng = CostCenter(code="CC-ENG", name="Engineering", description="R&D cost center", manager_id=created_users["MANAGER"].id)
        cc_sales = CostCenter(code="CC-SALES", name="Sales & Marketing", description="Customer acquisition expenses", manager_id=created_users["SALES"].id)
        session.add_all([cc_eng, cc_sales])
        await session.flush()

        # 4. Seed General Ledger Chart of Accounts
        # Root Assets Accounts (1000 - 1999)
        acc_cash = GeneralLedgerAccount(code="1000", name="Cash & Cash Equivalents", account_type="ASSET", opening_balance=500000.00, current_balance=500000.00)
        acc_ar = GeneralLedgerAccount(code="1200", name="Accounts Receivable", account_type="ASSET", opening_balance=0.00, current_balance=0.00)
        acc_inv = GeneralLedgerAccount(code="1400", name="Inventory Asset", account_type="ASSET", opening_balance=240000.00, current_balance=240000.00)
        acc_equip = GeneralLedgerAccount(code="1600", name="Fixed Asset Equipment", account_type="ASSET", opening_balance=10000.00, current_balance=10000.00)
        acc_accum_dep = GeneralLedgerAccount(code="1800", name="Accumulated Depreciation", account_type="ASSET", opening_balance=0.00, current_balance=0.00)
        
        # Liabilities Accounts (2000 - 2999)
        acc_ap = GeneralLedgerAccount(code="2000", name="Accounts Payable", account_type="LIABILITY", opening_balance=0.00, current_balance=0.00)
        acc_tax = GeneralLedgerAccount(code="2200", name="Tax Payable", account_type="LIABILITY", opening_balance=0.00, current_balance=0.00)
        
        # Equity Accounts (3000 - 3999)
        acc_equity = GeneralLedgerAccount(code="3000", name="Retained Earnings", account_type="EQUITY", opening_balance=750000.00, current_balance=750000.00)
        
        # Revenue Accounts (4000 - 4999)
        acc_revenue = GeneralLedgerAccount(code="4000", name="Sales Revenue", account_type="REVENUE", opening_balance=0.00, current_balance=0.00)
        
        # Expenses Accounts (5000 - 5999)
        acc_cogs = GeneralLedgerAccount(code="5000", name="Cost of Goods Sold", account_type="EXPENSE", opening_balance=0.00, current_balance=0.00)
        acc_rent = GeneralLedgerAccount(code="5100", name="Rent Expense", account_type="EXPENSE", opening_balance=0.00, current_balance=0.00)
        acc_dep_exp = GeneralLedgerAccount(code="5500", name="Depreciation Expense", account_type="EXPENSE", opening_balance=0.00, current_balance=0.00)

        session.add_all([acc_cash, acc_ar, acc_inv, acc_equip, acc_accum_dep, acc_ap, acc_tax, acc_equity, acc_revenue, acc_cogs, acc_rent, acc_dep_exp])
        await session.flush()

        # 5. Seed Tax Rules
        tax_config = TaxConfiguration(name="Default GST Configuration", code="GST", status="ACTIVE")
        session.add(tax_config)
        await session.flush()

        tax_rate = TaxRate(tax_configuration_id=tax_config.id, name="GST 18%", rate=18.0)
        session.add(tax_rate)

        # 6. Seed Expense Categories
        cat_travel = ExpenseCategory(name="Travel & Transport", code="TRAVEL", default_account_id=acc_rent.id)
        cat_meals = ExpenseCategory(name="Meals & Business Entertainment", code="MEALS", default_account_id=acc_rent.id)
        session.add_all([cat_travel, cat_meals])
        await session.flush()

        # --- Phase 6: PLATFORM SEEDS ---
        # 1. Seed Notification templates
        session.add_all([
            NotificationTemplate(name="Low Stock Alert", code="LOW_STOCK_ALERT", subject_template="Inventory Warning: Low stock on {{item_name}}", body_template="Warehouse stock alert. The item {{item_name}} quantity has dropped to {{current_quantity}}.", channels="IN_APP,EMAIL"),
            NotificationTemplate(name="Invoice Approval Required", code="INVOICE_APPROVAL", subject_template="Finance: Invoice Approval Required for {{invoice_num}}", body_template="Invoice {{invoice_num}} total of {{total}} requires approval reviews.", channels="IN_APP,EMAIL")
        ])

        # 2. Seed System Settings
        session.add_all([
            SystemSetting(key="email.smtp_host", value="smtp.businessos.com", category="EMAIL", description="Corporate SMTP Server Address"),
            SystemSetting(key="storage.local_path", value="C:/Users/meetc/Desktop/AI BusinessOS/storage/", category="STORAGE", description="File attachments system path"),
            SystemSetting(key="general.company_name", value="AI BusinessOS Enterprise Ltd", category="GENERAL", description="Company legal registration name")
        ])

        # 3. Seed Feature Flags
        session.add_all([
            FeatureFlag(name="experimental.ai_forecasting", enabled=False, description="Beta AI analytical forecasts visualizer"),
            FeatureFlag(name="ui.next_dashboard", enabled=True, description="Modern UI Dashboard workspace")
        ])

        # 4. Seed Scheduled Jobs
        session.add(ScheduledJob(
            name="Monthly straight-line depreciation run",
            code="DEPRECIATION_RUN",
            cron_expression="0 0 1 * *",
            status="ACTIVE",
            max_retries=3,
            backoff_seconds=60,
            dlq_flag=False
        ))

        # 5. Seed Telemetry Health metric
        session.add(HealthMetric(
            api_latency_ms=18.4,
            db_latency_ms=4.2,
            redis_connected=True,
            disk_usage_percent=42.5,
            memory_usage_percent=61.8,
            scheduler_queue_depth=0,
            email_queue_depth=0,
            workflow_queue_depth=0
        ))
        await session.flush()

        # --- Phase 7: ANALYTICS SEEDS ---
        # 1. Seed Business Metrics (Semantic definitions)
        bm_rev = BusinessMetric(name="Total Revenue", code="REVENUE", formula="SUM(invoices.total_amount)", dependencies_json={"tables": ["invoices"]}, cache_refresh_rate="HOURLY", description="Total revenue generated from active invoices")
        bm_gp = BusinessMetric(name="Gross Profit", code="GROSS_PROFIT", formula="REVENUE - expenses", dependencies_json={"tables": ["invoices", "vendor_bills"]}, cache_refresh_rate="DAILY", description="Net revenue margin minus vendor bill expenditures")
        bm_conv = BusinessMetric(name="Lead Conversion Rate", code="LEAD_CONVERSION_RATE", formula="COUNT(converted_leads) / COUNT(leads)", dependencies_json={"tables": ["leads"]}, cache_refresh_rate="REALTIME", description="Conversion rate of leads into opportunities")
        bm_hc = BusinessMetric(name="Employee Headcount", code="EMPLOYEE_HEADCOUNT", formula="COUNT(employees)", dependencies_json={"tables": ["employees"]}, cache_refresh_rate="DAILY", description="Active employee headcount count")
        session.add_all([bm_rev, bm_gp, bm_conv, bm_hc])
        await session.flush()

        # 2. Seed Dashboard layouts
        db_ceo = Dashboard(name="CEO Executive Dashboard", code="CEO_DASHBOARD", allowed_roles="SUPER_ADMIN,ADMIN,CEO", description="Corporate summarization for C-Suite reviews")
        session.add(db_ceo)
        await session.flush()

        # 3. Seed KPI Targets
        kpi_rev = KPIDefinition(name="Monthly Target Revenue", metric_code="REVENUE", target_value=500000.0, threshold_yellow=400000.0, threshold_red=250000.0, status="ACTIVE")
        kpi_conv = KPIDefinition(name="Target Conversion Rate", metric_code="LEAD_CONVERSION_RATE", target_value=30.0, threshold_yellow=25.0, threshold_red=15.0, status="ACTIVE")
        session.add_all([kpi_rev, kpi_conv])

        # 4. Seed Forecast Models
        fc_rev = ForecastModel(name="Baseline Revenue Exponential Fit", metric_code="REVENUE", model_type="LINEAR_REGRESSION", version=1, status="ACTIVE")
        session.add(fc_rev)
        await session.flush()

        # --- Phase 8: AI SEEDS ---
        # 1. Seed LLM Providers
        prov_openai = LLMProvider(name="OpenAI", code="OPENAI", api_endpoint="https://api.openai.com/v1", status="ACTIVE")
        session.add(prov_openai)
        await session.flush()

        # 2. Seed Model Configurations
        mc_gpt4 = ModelConfiguration(provider_id=prov_openai.id, model_name="gpt-4o", temperature=0.7, max_tokens=4096, is_default=True)
        session.add(mc_gpt4)

        # 3. Seed dynamic tool registries (MCP compatible)
        tool_query = ToolDefinition(
            name="run_analytics_query",
            description="Query dynamic calculated business metrics like revenue and headcount from the Metrics Engine",
            input_schema={"type": "object", "properties": {"metric_code": {"type": "string"}}},
            required_permissions="finance.ledger.read",
            timeout_seconds=30,
            retry_policy_max=3
        )
        tool_search = ToolDefinition(
            name="search_erp",
            description="Search dynamic indexed business entity profiles like customers and products using the Search Engine",
            input_schema={"type": "object", "properties": {"q": {"type": "string"}}},
            required_permissions="crm.customer.read",
            timeout_seconds=30,
            retry_policy_max=3
        )
        session.add_all([tool_query, tool_search])

        # 4. Seed dynamic Specialized Agents Registry
        session.add_all([
            AgentDefinition(name="Finance Agent", code="FINANCE_AGENT", capabilities="Analyze and query ledger accounts, balance sheets, and revenues", priority=1, version=1),
            AgentDefinition(name="Inventory Agent", code="INVENTORY_AGENT", capabilities="Track reorder thresholds, safety stock alerts, and warehouse lines", priority=1, version=1)
        ])

        await session.commit()
        logger.info("database_seeding_completed_successfully")

if __name__ == "__main__":
    asyncio.run(seed_database())
