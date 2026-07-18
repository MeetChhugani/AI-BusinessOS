from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException, ValidationException
from app.logging.config import logger
from app.models.finance import ExpenseClaim, JournalEntry, JournalEntryLine, LedgerRepository, JournalRepository
from app.models.hcm import Employee
from app.schemas.finance import ExpenseClaimCreate, ExpenseClaimResponse
from app.schemas.crm import ApprovalWorkflowAction

router = APIRouter(prefix="/expenses", tags=["Expense Claims"])

@router.get("", response_model=List[ExpenseClaimResponse], summary="List expense claims")
async def list_expenses(
    db: AsyncSession = Depends(get_db_session)
) -> List[ExpenseClaim]:
    query = select(ExpenseClaim).where(ExpenseClaim.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=ExpenseClaimResponse, status_code=201, summary="Submit corporate expense claim")
async def create_expense(
    body: ExpenseClaimCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ExpenseClaim:
    # Resolve Employee profile matching current user
    emp_q = select(Employee).where(Employee.user_id == current_user.id)
    emp_res = await db.execute(emp_q)
    emp = emp_res.scalars().first()
    if not emp:
        raise ValidationException("Only registered employees can submit expense claims")

    count_q = select(func.count(ExpenseClaim.id))
    count_res = await db.execute(count_q)
    total = count_res.scalar() or 0
    claim_num = f"EXP-{date.today().year}-{total + 1:05d}"

    claim = ExpenseClaim(
        claim_number=claim_num,
        employee_id=emp.id,
        expense_category_id=body.expense_category_id,
        amount=body.amount,
        claim_date=body.claim_date,
        description=body.description,
        receipt_image_url=body.receipt_image_url,
        status="SUBMITTED"
    )
    db.add(claim)
    
    # Auto-assign initial workflow approval step (Assigned to Admin user)
    # Fetch admin user to assign workflow
    admin_q = select(User).where(User.role == "ADMIN")
    adm_res = await db.execute(admin_q)
    admin = adm_res.scalars().first()
    if admin:
        from app.models.inventory import ApprovalWorkflow
        wf = ApprovalWorkflow(
            entity_type="EXPENSE_CLAIM",
            entity_id=claim.id,
            approver_id=admin.id,
            sequence_order=1,
            status="PENDING"
        )
        db.add(wf)
        
    await db.commit()
    await db.refresh(claim)
    logger.info("expense_claim_submitted", claim_number=claim_num)
    return claim

@router.post("/{id}/approve", response_model=ExpenseClaimResponse, summary="Approve expense claim and reimburse")
async def approve_expense(
    id: UUID,
    body: ApprovalWorkflowAction,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> ExpenseClaim:
    claim_q = select(ExpenseClaim).where(ExpenseClaim.id == id)
    claim_res = await db.execute(claim_q)
    claim = claim_res.scalars().first()
    if not claim:
        raise EntityNotFoundException("Expense Claim not found")

    if claim.status != "SUBMITTED":
        raise ValidationException("Claim is not pending approval")

    # Fetch active workflow step
    from app.models.inventory import ApprovalWorkflow
    wf_q = select(ApprovalWorkflow).where(
        and_(
            ApprovalWorkflow.entity_type == "EXPENSE_CLAIM",
            ApprovalWorkflow.entity_id == claim.id,
            ApprovalWorkflow.status == "PENDING"
        )
    )
    res = await db.execute(wf_q)
    wf = res.scalars().first()
    
    if wf:
        wf.status = "APPROVED" if body.approved else "REJECTED"
        wf.comments = body.comments
        wf.reviewed_at = func.now()

    if body.approved:
        claim.status = "APPROVED"
        
        # Post GL entry:
        # Expense GL Account Debit (+)
        # Cash/Bank GL Account Credit (-)
        exp_repo = LedgerRepository(db)
        # Fetch default account for Expense Category
        from app.models.finance import ExpenseCategory
        cat_q = select(ExpenseCategory).where(ExpenseCategory.id == claim.expense_category_id)
        cat_res = await db.execute(cat_q)
        category = cat_res.scalars().first()
        
        exp_acc_id = category.default_account_id if category else None
        cash_acc = await exp_repo.get_by_code("1000") # Cash/Bank Account
        
        if exp_acc_id and cash_acc:
            je_lines = [
                JournalEntryLine(account_id=exp_acc_id, debit=claim.amount, credit=0.0),
                JournalEntryLine(account_id=cash_acc.id, debit=0.0, credit=claim.amount)
            ]
            je = JournalEntry(
                entry_date=date.today(),
                description=f"Reimbursement for expense claim {claim.claim_number}",
                source_document=claim.claim_number,
                lines=je_lines
            )
            await JournalRepository(db).post_entry(je)
            claim.status = "REIMBURSED"
    else:
        claim.status = "REJECTED"

    await db.commit()
    await db.refresh(claim)
    return claim
from datetime import date
from app.models.user import User
