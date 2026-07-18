import uuid
from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class AlertRule(AuditBase):
    __tablename__ = "analytics_alert_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_code: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. CASH_RESERVE
    operator: Mapped[str] = mapped_column(String(20), default="LT") # LT, GT, EQ
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")

class AlertExecution(AuditBase):
    __tablename__ = "analytics_alert_executions"

    rule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_alert_rules.id", ondelete="CASCADE"), nullable=False)
    triggered_value: Mapped[float] = mapped_column(Float, nullable=False)
    workflow_execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(30), default="TRIGGERED")
