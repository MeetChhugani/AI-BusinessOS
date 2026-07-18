import uuid
from typing import Optional
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class SystemSetting(AuditBase):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False) # e.g. email.smtp_host
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="GENERAL") # GENERAL, SECURITY, EMAIL, STORAGE, FINANCE
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

class FeatureFlag(AuditBase):
    __tablename__ = "feature_flags"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False) # e.g. BETA_DASHBOARD
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    rules: Mapped[Optional[str]] = mapped_column(Text) # JSON configuration of targeting rules (roles, tenants, etc.)
    description: Mapped[Optional[str]] = mapped_column(Text)
