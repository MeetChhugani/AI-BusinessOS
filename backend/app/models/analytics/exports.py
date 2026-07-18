import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class DataExport(AuditBase):
    __tablename__ = "analytics_data_exports"

    export_type: Mapped[str] = mapped_column(String(30), nullable=False) # CSV, PDF, JSON
    file_metadata_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete="SET NULL"))
    triggered_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED")
