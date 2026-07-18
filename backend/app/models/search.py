import uuid
from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class SearchIndex(AuditBase):
    __tablename__ = "search_indexes"

    entity_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # Employee, Product, Invoice
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text) # Comma-separated list
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)
