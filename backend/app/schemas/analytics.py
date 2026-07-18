from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class DashboardWidgetResponse(BaseModel):
    id: UUID
    dashboard_id: UUID
    title: str
    widget_type: str
    size_x: int
    size_y: int
    position_x: int
    position_y: int
    query_config: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class DashboardResponse(BaseModel):
    id: UUID
    name: str
    code: str
    allowed_roles: str
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class KPIDefinitionResponse(BaseModel):
    id: UUID
    name: str
    metric_code: str
    target_value: float
    threshold_yellow: float
    threshold_red: float
    status: str
    model_config = ConfigDict(from_attributes=True)

class KPIValueResponse(BaseModel):
    id: UUID
    kpi_id: UUID
    current_value: float
    status_indicator: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AnalyticsQueryRequest(BaseModel):
    metric_code: str
    dimensions: List[str] = []
    filters: Dict[str, Any] = {}

class AnalyticsQueryResponse(BaseModel):
    metric: str
    value: float
    dimensions: List[str]
    filters: Dict[str, Any]
    timestamp: str

class DeterministicInsightResponse(BaseModel):
    category: str
    severity: str
    message: str
    action_url: Optional[str] = None

class ForecastResultResponse(BaseModel):
    date: str
    value: float
    lower: float
    upper: float
