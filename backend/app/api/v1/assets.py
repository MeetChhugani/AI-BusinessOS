from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.logging.config import logger
from app.models.finance import Asset, AssetDepreciation
from app.repositories.finance_repository import AssetRepository
from app.schemas.finance import AssetCreate, AssetResponse

router = APIRouter(prefix="/assets", tags=["Fixed Assets"])

@router.get("", response_model=List[AssetResponse], summary="List fixed assets")
async def list_assets(
    db: AsyncSession = Depends(get_db_session)
) -> List[Asset]:
    query = select(Asset).where(Asset.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=AssetResponse, status_code=201, summary="Register asset purchase")
async def create_asset(
    body: AssetCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
) -> Asset:
    # Generate asset sequence number
    count_q = select(func.count(Asset.id))
    count_res = await db.execute(count_q)
    total = count_res.scalar() or 0
    asset_num = f"AST-{date.today().year}-{total + 1:04d}"

    asset = Asset(
        asset_number=asset_num,
        name=body.name,
        category=body.category,
        purchase_date=body.purchase_date,
        purchase_value=body.purchase_value,
        residual_value=body.residual_value,
        useful_life_months=body.useful_life_months,
        asset_account_id=body.asset_account_id,
        depreciation_account_id=body.depreciation_account_id,
        status="ACTIVE"
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    logger.info("fixed_asset_registered", asset_number=asset_num)
    return asset

@router.post("/{id}/depreciate", status_code=201, summary="Trigger monthly straight-line depreciation run")
async def run_depreciation(
    id: UUID,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "FINANCE_MANAGER"])),
    db: AsyncSession = Depends(get_db_session)
):
    repo = AssetRepository(db)
    dep = await repo.calculate_depreciation(id)
    return dep
from sqlalchemy import func
from datetime import date
