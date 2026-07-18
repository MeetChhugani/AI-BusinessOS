import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class ScheduledJob(AuditBase):
    __tablename__ = "scheduled_jobs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. DEPRECIATION_RUN
    cron_expression: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 0 0 1 * *
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE") # ACTIVE, INACTIVE
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Retry Policy configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    backoff_seconds: Mapped[int] = mapped_column(Integer, default=60)
    dlq_flag: Mapped[bool] = mapped_column(Boolean, default=False)

class JobExecution(AuditBase):
    __tablename__ = "job_executions"

    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scheduled_jobs.id", ondelete="CASCADE"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="RUNNING") # RUNNING, SUCCESS, FAILED, RETRYING
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
