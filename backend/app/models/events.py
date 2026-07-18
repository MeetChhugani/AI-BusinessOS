import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class SystemEvent(AuditBase):
    __tablename__ = "system_events"

    event_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. sales_order_approved
    correlation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    parent_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    version: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PROCESSED") # PROCESSED, FAILED
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
