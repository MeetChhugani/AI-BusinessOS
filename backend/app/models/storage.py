import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class FileFolder(AuditBase):
    __tablename__ = "file_folders"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("file_folders.id", ondelete="CASCADE"))
    path: Mapped[str] = mapped_column(String(512), nullable=False) # e.g. /invoices

class FileMetadata(AuditBase):
    __tablename__ = "file_metadata"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("file_folders.id", ondelete="SET NULL"))
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False) # local file path or cloud URI
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    uploaded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
