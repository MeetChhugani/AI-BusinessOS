import uuid
from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class KPIDefinition(AuditBase):
    __tablename__ = "analytics_kpi_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_yellow: Mapped[float] = mapped_column(Float, nullable=False) # values below this are yellow
    threshold_red: Mapped[float] = mapped_column(Float, nullable=False) # values below this are red
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")

class KPIValue(AuditBase):
    __tablename__ = "analytics_kpi_values"

    kpi_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_kpi_definitions.id", ondelete="CASCADE"), nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    status_indicator: Mapped[str] = mapped_column(String(20), default="GREEN") # GREEN, YELLOW, RED
