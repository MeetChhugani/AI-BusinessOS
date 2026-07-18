import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class Dashboard(AuditBase):
    __tablename__ = "analytics_dashboards"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. CEO_DASHBOARD
    allowed_roles: Mapped[str] = mapped_column(String(255), default="SUPER_ADMIN,ADMIN,CEO") # Comma-separated
    description: Mapped[Optional[str]] = mapped_column(Text)

class DashboardWidget(AuditBase):
    __tablename__ = "analytics_dashboard_widgets"

    dashboard_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_dashboards.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    widget_type: Mapped[str] = mapped_column(String(50), nullable=False) # line, bar, pie, card, gauge
    size_x: Mapped[int] = mapped_column(default=1)
    size_y: Mapped[int] = mapped_column(default=1)
    position_x: Mapped[int] = mapped_column(default=0)
    position_y: Mapped[int] = mapped_column(default=0)
    query_config: Mapped[dict] = mapped_column(JSONB, nullable=False) # e.g. {"metric": "revenue", "range": "30d"}

class SavedDashboard(AuditBase):
    __tablename__ = "analytics_saved_dashboards"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dashboard_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analytics_dashboards.id", ondelete="CASCADE"), nullable=False)
    layout_state: Mapped[Optional[dict]] = mapped_column(JSONB)

class VisualizationTemplate(AuditBase):
    __tablename__ = "analytics_visualization_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    chart_library: Mapped[str] = mapped_column(String(50), default="recharts")
    default_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
