import uuid
from typing import Optional
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class HealthMetric(AuditBase):
    __tablename__ = "health_metrics"

    api_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    db_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    redis_connected: Mapped[bool] = mapped_column(default=True)
    disk_usage_percent: Mapped[float] = mapped_column(Float, default=0.0)
    memory_usage_percent: Mapped[float] = mapped_column(Float, default=0.0)
    scheduler_queue_depth: Mapped[int] = mapped_column(Integer, default=0)
    email_queue_depth: Mapped[int] = mapped_column(Integer, default=0)
    workflow_queue_depth: Mapped[int] = mapped_column(Integer, default=0)
