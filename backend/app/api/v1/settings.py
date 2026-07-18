from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.models.settings import SystemSetting
from app.models.health import HealthMetric
from app.schemas.platform import SystemSettingResponse, HealthMetricResponse

router = APIRouter(prefix="/settings", tags=["System Settings & Health"])

@router.get("", response_model=List[SystemSettingResponse], summary="List administrative system configurations")
async def list_settings(
    db: AsyncSession = Depends(get_db_session)
) -> List[SystemSetting]:
    query = select(SystemSetting).where(SystemSetting.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/{key}", response_model=SystemSettingResponse, summary="Modify system setting key value")
async def update_setting(
    key: str,
    value: str,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
) -> SystemSetting:
    q = select(SystemSetting).where(SystemSetting.key == key)
    res = await db.execute(q)
    setting = res.scalars().first()
    if not setting:
        setting = SystemSetting(key=key, value=value)
    else:
        setting.value = value

    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return setting

@router.get("/health", response_model=List[HealthMetricResponse], summary="Fetch system API latency and queues telemetry data")
async def get_health(
    db: AsyncSession = Depends(get_db_session)
):
    query = select(HealthMetric).order_by(HealthMetric.created_at.desc()).limit(10)
    res = await db.execute(query)
    return list(res.scalars().all())
