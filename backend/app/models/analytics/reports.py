import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class ReportDefinition(AuditBase):
    __tablename__ = "analytics_report_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    columns_config: Mapped[dict] = mapped_column(JSONB, nullable=False) # e.g. ["date", "salesperson", "total"]
    filters_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    groupings_config: Mapped[Optional[dict]] = mapped_column(JSONB)

class ReportExecution(AuditBase):
    __tablename__ = "analytics_report_executions"

    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_report_definitions.id", ondelete="CASCADE"), nullable=False)
    run_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    execution_time_ms: Mapped[int] = mapped_column(default=0)
    results_count: Mapped[int] = mapped_column(default=0)

class ScheduledReport(AuditBase):
    __tablename__ = "analytics_scheduled_reports"

    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_report_definitions.id", ondelete="CASCADE"), nullable=False)
    frequency: Mapped[str] = mapped_column(String(30), default="DAILY") # DAILY, WEEKLY, MONTHLY
    recipient_emails: Mapped[str] = mapped_column(Text, nullable=False) # comma-separated
    export_format: Mapped[str] = mapped_column(String(10), default="CSV") # CSV, PDF

class DrilldownConfiguration(AuditBase):
    __tablename__ = "analytics_drilldown_configurations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hierarchy_path: Mapped[dict] = mapped_column(JSONB, nullable=False) # e.g. ["department", "salesperson", "invoice"]
