import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class BusinessMetric(AuditBase):
    __tablename__ = "analytics_business_metrics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. REVENUE
    formula: Mapped[str] = mapped_column(Text, nullable=False) # e.g. SUM(invoices.total)
    dependencies_json: Mapped[dict] = mapped_column(JSONB, default=dict) # e.g. {"tables": ["invoices", "payments"]}
    cache_refresh_rate: Mapped[str] = mapped_column(String(50), default="HOURLY") # DAILY, HOURLY, REALTIME
    description: Mapped[Optional[str]] = mapped_column(Text)

class BusinessDimension(AuditBase):
    __tablename__ = "analytics_business_dimensions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. DEPARTMENT, REGION
    table_reference: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. departments
    field_reference: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. name

class MetricDefinition(AuditBase):
    __tablename__ = "analytics_metric_definitions"

    metric_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_business_metrics.id", ondelete="CASCADE"), nullable=False)
    aggregation_type: Mapped[str] = mapped_column(String(30), default="SUM") # SUM, AVG, COUNT
    filters_config: Mapped[Optional[dict]] = mapped_column(JSONB)

class MetricSnapshot(AuditBase):
    __tablename__ = "analytics_metric_snapshots"

    metric_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_business_metrics.id", ondelete="CASCADE"), nullable=False)
    snapshot_value: Mapped[float] = mapped_column(default=0.0)
    dimensions_payload: Mapped[Optional[dict]] = mapped_column(JSONB) # e.g. {"department": "Engineering"}
