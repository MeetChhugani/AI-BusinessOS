import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Dict
from sqlalchemy import and_, select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.exceptions.custom_exceptions import ValidationException, EntityNotFoundException
from app.logging.config import logger
from app.models.finance import (
    GeneralLedgerAccount,
    JournalEntry,
    JournalEntryLine,
    FiscalPeriod,
    CustomerInvoice,
    InvoiceItem,
    VendorBill,
    VendorBillItem,
    Payment,
    PaymentAllocation,
    Asset,
    AssetDepreciation,
    Budget,
    BudgetLine,
    CostCenter,
)

class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

class LedgerRepository(BaseRepository):
    async def get_accounts(self) -> List[GeneralLedgerAccount]:
        query = select(GeneralLedgerAccount).where(GeneralLedgerAccount.deleted_at.is_(None)).order_by(GeneralLedgerAccount.code)
        res = await self.db.execute(query)
        return list(res.scalars().all())

    async def get_by_code(self, code: str) -> Optional[GeneralLedgerAccount]:
        query = select(GeneralLedgerAccount).where(and_(GeneralLedgerAccount.code == code, GeneralLedgerAccount.deleted_at.is_(None)))
        res = await self.db.execute(query)
        return res.scalars().first()

    async def create_account(self, acc: GeneralLedgerAccount) -> GeneralLedgerAccount:
        self.db.add(acc)
        await self.db.commit()
        await self.db.refresh(acc)
        return acc

class JournalRepository(BaseRepository):
    async def post_entry(self, entry: JournalEntry, request_id: Optional[str] = None) -> JournalEntry:
        # 1. Validate target period status (Open vs Closed/Locked)
        period_q = select(FiscalPeriod).where(
            and_(
                FiscalPeriod.start_date <= entry.entry_date,
                FiscalPeriod.end_date >= entry.entry_date,
                FiscalPeriod.deleted_at.is_(None)
            )
        )
        period_res = await self.db.execute(period_q)
        period = period_res.scalars().first()
        if not period:
            raise ValidationException("No matching Fiscal Period found for transaction date")
        if period.status != "OPEN":
            raise ValidationException(f"Cannot post to a closed or locked period: {period.name} ({period.status})")

        # 2. Verify double-entry rules: debits == credits
        total_debits = sum(line.debit for line in entry.lines)
        total_credits = sum(line.credit for line in entry.lines)
        if abs(total_debits - total_credits) > 0.01:
            raise ValidationException(f"Unbalanced journal entry: Total Debits (${total_debits}) must equal Total Credits (${total_credits})")

        # 3. Generate human-readable sequence number
        count_q = select(func.count(JournalEntry.id))
        count_res = await self.db.execute(count_q)
        total = count_res.scalar() or 0
        year = entry.entry_date.year
        entry.entry_number = f"JE-{year}-{total + 1:06d}"
        entry.status = "POSTED"

        # Update GL account balances
        for line in entry.lines:
            acc_q = select(GeneralLedgerAccount).where(GeneralLedgerAccount.id == line.account_id)
            acc_res = await self.db.execute(acc_q)
            account = acc_res.scalars().first()
            if account:
                # Add debit or subtract credit depending on asset vs liability account types
                if account.account_type in ["ASSET", "EXPENSE"]:
                    account.current_balance += (line.debit - line.credit)
                else:
                    account.current_balance += (line.credit - line.debit)
                self.db.add(account)

        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        logger.info("journal_entry_posted", entry_number=entry.entry_number, total=float(total_debits))
        return entry

class InvoiceRepository(BaseRepository):
    async def create_from_sales_order(self, sales_order_id: uuid.UUID) -> CustomerInvoice:
        # Import dynamically to prevent circular dependencies
        from app.models.crm import SalesOrder
        so_q = select(SalesOrder).where(SalesOrder.id == sales_order_id).options(selectinload(SalesOrder.items))
        so_res = await self.db.execute(so_q)
        so = so_res.scalars().first()
        if not so:
            raise EntityNotFoundException("Sales Order not found")

        # Calculate Due date based on payment terms (NET30, NET45, End of month, etc)
        issue_date = date.today()
        due_days = 30
        if so.customer.payment_terms == "NET15":
            due_days = 15
        elif so.customer.payment_terms == "NET45":
            due_days = 45
        elif so.customer.payment_terms == "NET60":
            due_days = 60
        elif so.customer.payment_terms == "IMMEDIATE":
            due_days = 0
        due_date = issue_date + timedelta(days=due_days)

        # Generate invoice number
        count_q = select(func.count(CustomerInvoice.id))
        count_res = await self.db.execute(count_q)
        total = count_res.scalar() or 0
        inv_num = f"INV-{issue_date.year}-{total + 1:06d}"

        items_list = []
        for item in so.items:
            items_list.append(
                InvoiceItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_cost=item.total_cost
                )
            )

        invoice = CustomerInvoice(
            invoice_number=inv_num,
            customer_id=so.customer_id,
            sales_order_id=so.id,
            issue_date=issue_date,
            due_date=due_date,
            payment_terms=so.customer.payment_terms,
            subtotal=so.subtotal,
            tax_amount=so.tax_amount,
            discount_amount=so.discount_amount,
            total_amount=so.total_amount,
            outstanding_balance=so.total_amount,
            status="APPROVED",
            items=items_list
        )
        self.db.add(invoice)
        await self.db.flush()

        # Automatic double entry posting:
        # Accounts Receivable (Asset) Debit (+)
        # Sales Revenue (Revenue) Credit (+)
        ar_acc = await LedgerRepository(self.db).get_by_code("1200") # Accounts Receivable Account
        revenue_acc = await LedgerRepository(self.db).get_by_code("4000") # Sales Revenue Account

        if ar_acc and revenue_acc:
            je_lines = [
                JournalEntryLine(account_id=ar_acc.id, debit=invoice.total_amount, credit=0.0),
                JournalEntryLine(account_id=revenue_acc.id, debit=0.0, credit=invoice.total_amount)
            ]
            je = JournalEntry(
                entry_date=issue_date,
                description=f"Automated entry for customer invoice {inv_num}",
                source_document=inv_num,
                lines=je_lines
            )
            await JournalRepository(self.db).post_entry(je)

        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

class PaymentRepository(BaseRepository):
    async def record_payment(self, payment: Payment) -> Payment:
        count_q = select(func.count(Payment.id))
        count_res = await self.db.execute(count_q)
        total = count_res.scalar() or 0
        payment.payment_number = f"PAY-{date.today().year}-{total + 1:06d}"
        
        self.db.add(payment)
        await self.db.flush()

        # Update matching invoices or bills balances
        for alloc in payment.allocations:
            if alloc.invoice_id:
                inv_q = select(CustomerInvoice).where(CustomerInvoice.id == alloc.invoice_id)
                inv_res = await self.db.execute(inv_q)
                inv = inv_res.scalars().first()
                if inv:
                    inv.outstanding_balance = max(0.0, float(inv.outstanding_balance) - float(alloc.allocated_amount))
                    if inv.outstanding_balance == 0.0:
                        inv.status = "PAID"
                    else:
                        inv.status = "PARTIALLY_PAID"
                    self.db.add(inv)

                    # Post GL Journal Entry for Inflow Cash:
                    # Bank GL account (Asset) Debit (+)
                    # Accounts Receivable (Asset) Credit (-)
                    bank_acc = await LedgerRepository(self.db).get_by_code("1000")
                    ar_acc = await LedgerRepository(self.db).get_by_code("1200")
                    if bank_acc and ar_acc:
                        je_lines = [
                            JournalEntryLine(account_id=bank_acc.id, debit=alloc.allocated_amount, credit=0.0),
                            JournalEntryLine(account_id=ar_acc.id, debit=0.0, credit=alloc.allocated_amount)
                        ]
                        je = JournalEntry(
                            entry_date=payment.payment_date,
                            description=f"Cash payment collection receipt for invoice {inv.invoice_number}",
                            source_document=payment.payment_number,
                            lines=je_lines
                        )
                        await JournalRepository(self.db).post_entry(je)

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

class AssetRepository(BaseRepository):
    async def calculate_depreciation(self, asset_id: uuid.UUID) -> AssetDepreciation:
        asset_q = select(Asset).where(Asset.id == asset_id)
        asset_res = await self.db.execute(asset_q)
        asset = asset_res.scalars().first()
        if not asset or asset.status != "ACTIVE":
            raise EntityNotFoundException("Asset not found or not active")

        # Straight-line depreciation calculation:
        # Amount = (Purchase Value - Residual Value) / Useful Life Months
        depreciable_base = float(asset.purchase_value) - float(asset.residual_value)
        monthly_dep_amount = depreciable_base / float(asset.useful_life_months)

        # Check existing accumulative depreciations
        accum_q = select(func.sum(AssetDepreciation.amount)).where(AssetDepreciation.asset_id == asset.id)
        accum_res = await self.db.execute(accum_q)
        accumulated = float(accum_res.scalar() or 0.0)

        if accumulated >= depreciable_base:
            asset.status = "FULLY_DEPRECIATED"
            self.db.add(asset)
            await self.db.commit()
            raise ValidationException("Asset is already fully depreciated")

        new_accum = accumulated + monthly_dep_amount
        dep_date = date.today()

        # Post depreciation double-entry JEs:
        # Depreciation Expense Debit (+)
        # Accumulated Depreciation Credit (+)
        dep_exp_acc = await LedgerRepository(self.db).get_by_code("5500") # Depreciation Expense Account
        accum_dep_acc = await LedgerRepository(self.db).get_by_code("1800") # Accumulated Depreciation Account

        je_id = None
        if dep_exp_acc and accum_dep_acc:
            je_lines = [
                JournalEntryLine(account_id=dep_exp_acc.id, debit=monthly_dep_amount, credit=0.0),
                JournalEntryLine(account_id=accum_dep_acc.id, debit=0.0, credit=monthly_dep_amount)
            ]
            je = JournalEntry(
                entry_date=dep_date,
                description=f"Monthly straight-line depreciation run for asset {asset.asset_number}",
                source_document=asset.asset_number,
                lines=je_lines
            )
            posted = await JournalRepository(self.db).post_entry(je)
            je_id = posted.id

        dep = AssetDepreciation(
            asset_id=asset.id,
            depreciation_date=dep_date,
            amount=monthly_dep_amount,
            accumulated_depreciation=new_accum,
            journal_entry_id=je_id
        )
        self.db.add(dep)
        await self.db.commit()
        return dep

class FinancialReportRepository(BaseRepository):
    async def get_trial_balance(self) -> List[Dict]:
        accounts = await LedgerRepository(self.db).get_accounts()
        report = []
        for acc in accounts:
            debit = float(acc.current_balance) if acc.account_type in ["ASSET", "EXPENSE"] else 0.0
            credit = float(acc.current_balance) if acc.account_type not in ["ASSET", "EXPENSE"] else 0.0
            report.append({
                "code": acc.code,
                "name": acc.name,
                "type": acc.account_type,
                "debit": debit,
                "credit": credit
            })
        return report

    async def get_profit_loss(self) -> Dict:
        accounts = await LedgerRepository(self.db).get_accounts()
        revenue = 0.0
        expenses = 0.0
        details = []

        for acc in accounts:
            if acc.account_type == "REVENUE":
                revenue += float(acc.current_balance)
                details.append({"code": acc.code, "name": acc.name, "amount": float(acc.current_balance)})
            elif acc.account_type == "EXPENSE":
                expenses += float(acc.current_balance)
                details.append({"code": acc.code, "name": acc.name, "amount": -float(acc.current_balance)})

        return {
            "total_revenue": revenue,
            "total_expenses": expenses,
            "net_income": revenue - expenses,
            "breakdown": details
        }
