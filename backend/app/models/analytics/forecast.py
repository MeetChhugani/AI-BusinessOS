import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class ForecastModel(AuditBase):
    __tablename__ = "analytics_forecast_models"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_code: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. REVENUE
    model_type: Mapped[str] = mapped_column(String(50), default="LINEAR_REGRESSION") # LINEAR_REGRESSION, EXPONENTIAL_SMOOTHING
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")

class ForecastResult(AuditBase):
    __tablename__ = "analytics_forecast_results"

    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_forecast_models.id", ondelete="CASCADE"), nullable=False)
    target_date: Mapped[datetime] = mapped_column(nullable=False)
    forecasted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_lower: Mapped[Optional[float]] = mapped_column(Float)
    confidence_upper: Mapped[Optional[float]] = mapped_column(Float)
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
