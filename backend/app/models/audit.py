import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class AuditEvent(AuditBase):
    __tablename__ = "audit_events"

    entity_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. Employee, Customer
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    operation: Mapped[str] = mapped_column(String(50), nullable=False) # CREATE, UPDATE, DELETE, POST
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    
    # Operation Source details
    source: Mapped[str] = mapped_column(String(50), default="API") # API, SCHEDULER, WORKFLOW, AI, MANUAL
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    request_id: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    browser: Mapped[Optional[str]] = mapped_column(String(255))
    reason: Mapped[Optional[str]] = mapped_column(String(512))

class AuditChange(AuditBase):
    __tablename__ = "audit_changes"

    audit_event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_events.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
