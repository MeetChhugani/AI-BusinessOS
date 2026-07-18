import uuid
from typing import Optional
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class NotificationTemplate(AuditBase):
    __tablename__ = "notification_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g. LOW_STOCK_ALERT
    subject_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    channels: Mapped[str] = mapped_column(String(255), default="IN_APP,EMAIL") # comma-separated list of enabled channels

class NotificationPreference(AuditBase):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. SECURITY, INVENTORY, FINANCE
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

class NotificationLog(AuditBase):
    __tablename__ = "notification_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="IN_APP") # IN_APP, EMAIL, SMS, WHATSAPP, PUSH
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL") # LOW, NORMAL, HIGH, URGENT
    delivery_status: Mapped[str] = mapped_column(String(30), default="SENT") # PENDING, SENT, FAILED
    read_status: Mapped[bool] = mapped_column(Boolean, default=False)
    retry_count: Mapped[int] = mapped_column(default=0)
