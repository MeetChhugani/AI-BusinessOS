from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.logging.config import logger
from app.models.inventory import Supplier
from app.schemas.inventory import SupplierCreate, SupplierResponse

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.get("", response_model=List[SupplierResponse], summary="List suppliers directory")
async def list_suppliers(
    db: AsyncSession = Depends(get_db_session)
) -> List[Supplier]:
    query = select(Supplier).where(Supplier.deleted_at.is_(None))
    result = await db.execute(query.order_by(Supplier.name))
    return list(result.scalars().all())

@router.post("", response_model=SupplierResponse, status_code=201, summary="Create a new supplier")
async def create_supplier(
    body: SupplierCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "INVENTORY_MANAGER", "PURCHASE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Supplier:
    new_sup = Supplier(
        name=body.name,
        code=body.code,
        contact_name=body.contact_name,
        email=body.email,
        phone=body.phone,
        gst_number=body.gst_number,
        address=body.address,
        payment_terms=body.payment_terms,
        rating=body.rating,
        status=body.status,
    )
    db.add(new_sup)
    await db.commit()
    await db.refresh(new_sup)
    logger.info("supplier_created", name=new_sup.name, code=new_sup.code)
    return new_sup

@router.get("/{id}/score", summary="Get Supplier Performance metrics score")
async def get_supplier_score(
    id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    query = select(Supplier).where(Supplier.id == id)
    res = await db.execute(query)
    sup = res.scalars().first()
    if not sup:
        raise EntityNotFoundException("Supplier not found")
        
    # Calculate score logic: 100 - (defect_rate * 2) - (cancellation_rate * 3) - (late_delivery_count * 5)
    score = 100.0 - (sup.defect_rate * 2.0) - (sup.cancellation_rate * 3.0) - (sup.late_delivery_count * 5.0)
    score = max(0.0, min(100.0, score))
    
    return {
        "supplier_id": str(id),
        "name": sup.name,
        "rating": sup.rating,
        "late_deliveries": sup.late_delivery_count,
        "defect_rate": sup.defect_rate,
        "cancellation_rate": sup.cancellation_rate,
        "supplier_performance_score": round(score, 2),
        "score_category": "EXCELLENT" if score >= 90 else "GOOD" if score >= 75 else "POOR"
    }
