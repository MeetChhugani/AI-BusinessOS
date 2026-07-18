from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.models.settings import FeatureFlag
from app.schemas.platform import FeatureFlagResponse

router = APIRouter(prefix="/features", tags=["Beta Feature Flags"])

@router.get("", response_model=List[FeatureFlagResponse], summary="List experimental feature flags")
async def list_features(
    db: AsyncSession = Depends(get_db_session)
) -> List[FeatureFlag]:
    query = select(FeatureFlag).where(FeatureFlag.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/{id}/toggle", response_model=FeatureFlagResponse, summary="Toggle beta feature flag activation state")
async def toggle_feature(
    id: UUID,
    enabled: bool,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
) -> FeatureFlag:
    q = select(FeatureFlag).where(FeatureFlag.id == id)
    res = await db.execute(q)
    flag = res.scalars().first()
    if not flag:
        raise EntityNotFoundException("Feature flag not found")

    flag.enabled = enabled
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return flag
