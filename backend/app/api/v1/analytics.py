from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.database.session import get_db_session
from app.models.analytics.dashboard import Dashboard
from app.models.analytics.kpis import KPIDefinition
from app.services.analytics_service import AnalyticsQueryEngine, InsightsEngine, ForecastEngine, KPIEngine
from app.schemas.analytics import (
    AnalyticsQueryRequest, AnalyticsQueryResponse,
    DeterministicInsightResponse, DashboardResponse,
    KPIDefinitionResponse, ForecastResultResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics & BI Platform"])

@router.post("/query", response_model=AnalyticsQueryResponse, summary="Query semantic business metrics")
async def query_metrics(
    body: AnalyticsQueryRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    return await AnalyticsQueryEngine.execute_query(
        db,
        metric_code=body.metric_code,
        dimensions=body.dimensions,
        filters=body.filters
    )

@router.get("/insights", response_model=List[DeterministicInsightResponse], summary="Fetch deterministic system insights")
async def get_insights(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    return await InsightsEngine.generate_deterministic_insights(db)

@router.get("/dashboards", response_model=List[DashboardResponse], summary="List allowed dashboards for user role")
async def list_dashboards(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[Dashboard]:
    query = select(Dashboard).where(Dashboard.deleted_at.is_(None))
    res = await db.execute(query)
    all_dashboards = res.scalars().all()
    
    # Filter dashboards by allowed roles permissions
    user_role = current_user.role
    filtered = [
        d for d in all_dashboards
        if user_role in [r.strip() for r in d.allowed_roles.split(",")]
    ]
    return filtered

@router.get("/kpis", response_model=List[KPIDefinitionResponse], summary="List configured KPI definitions")
async def list_kpis(
    db: AsyncSession = Depends(get_db_session)
) -> List[KPIDefinition]:
    query = select(KPIDefinition).where(KPIDefinition.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/forecasts", response_model=List[ForecastResultResponse], summary="Statistical metric trend forecasting")
async def get_forecast(
    metric_code: str = Query(..., description="Target metric e.g. REVENUE"),
    steps: int = Query(6, description="Forecast monthly steps"),
    db: AsyncSession = Depends(get_db_session)
):
    return await ForecastEngine.generate_baseline_forecast(db, metric_code, steps)
