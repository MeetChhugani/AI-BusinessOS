from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker, get_current_user
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import PermissionDeniedException, EntityNotFoundException
from app.logging.config import logger
from app.models.hcm import Employee, PerformanceReview
from app.models.user import User
from app.schemas.hcm import PerformanceReviewCreate, PerformanceReviewResponse

router = APIRouter(prefix="/performance", tags=["Performance"])

@router.get("", response_model=List[PerformanceReviewResponse], summary="List performance reviews")
async def list_reviews(
    employee_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[PerformanceReview]:
    query = select(PerformanceReview).where(PerformanceReview.deleted_at.is_(None))
    
    if current_user.role in ("SUPER_ADMIN", "ADMIN", "HR"):
        if employee_id:
            query = query.where(PerformanceReview.employee_id == employee_id)
            
    elif current_user.role == "MANAGER":
        # Fetch manager profile
        q = select(Employee).where(and_(Employee.user_id == current_user.id, Employee.deleted_at.is_(None)))
        r = await db.execute(q)
        manager = r.scalars().first()
        if not manager:
            return []
            
        if employee_id:
            # Check if direct report
            target_query = select(Employee).where(and_(Employee.id == employee_id, Employee.deleted_at.is_(None)))
            target_res = await db.execute(target_query)
            target = target_res.scalars().first()
            if not target or target.manager_id != manager.id:
                raise PermissionDeniedException("You can only access performance reviews for your direct reports")
            query = query.where(PerformanceReview.employee_id == employee_id)
        else:
            # Fetch reviews reviewer == manager or employee direct report
            query = query.join(Employee, Employee.id == PerformanceReview.employee_id).where(
                Employee.manager_id == manager.id
            )
            
    else:
        # Standard employee sees own reviews
        q = select(Employee).where(and_(Employee.user_id == current_user.id, Employee.deleted_at.is_(None)))
        r = await db.execute(q)
        emp = r.scalars().first()
        if not emp:
            return []
        query = query.where(PerformanceReview.employee_id == emp.id)

    result = await db.execute(query)
    return list(result.scalars().all())

@router.post("/{employee_id}", response_model=PerformanceReviewResponse, status_code=201, summary="Submit a new performance review")
async def submit_review(
    employee_id: UUID,
    body: PerformanceReviewCreate,
    current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HR", "MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> PerformanceReview:
    # Verify reviewer exists
    query = select(Employee).where(and_(Employee.id == employee_id, Employee.deleted_at.is_(None)))
    res = await db.execute(query)
    employee = res.scalars().first()
    if not employee:
        raise EntityNotFoundException("Target employee profile not found")

    review = PerformanceReview(
        employee_id=employee_id,
        reviewer_id=body.reviewer_id,
        review_cycle=body.review_cycle,
        rating=body.rating,
        goals=body.goals,
        achievements=body.achievements,
        strengths=body.strengths,
        weaknesses=body.weaknesses,
        manager_feedback=body.manager_feedback,
        self_review=body.self_review,
        promotion_recommendation=body.promotion_recommendation,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    logger.info("performance_review_submitted", employee_id=str(employee_id), rating=body.rating)
    return review
