import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class WorkflowDefinition(AuditBase):
    __tablename__ = "workflow_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. INVOICE_APPROVAL_LIMIT
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE") # ACTIVE, INACTIVE, DRAFT

class WorkflowTrigger(AuditBase):
    __tablename__ = "workflow_triggers"

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(100), nullable=False) # EVENT_DRIVEN, TIME_BASED, MANUAL
    event_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. INVENTORY_LEVEL_ALERT
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB)

class WorkflowCondition(AuditBase):
    __tablename__ = "workflow_conditions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False)
    operator: Mapped[str] = mapped_column(String(20), default="AND") # AND, OR
    expression: Mapped[dict] = mapped_column(JSONB, nullable=False) # e.g. {"field": "quantity", "op": "LT", "value": "safety_stock"}

class WorkflowAction(AuditBase):
    __tablename__ = "workflow_actions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False) # NOTIFY, SEND_EMAIL, APPROVAL, CALL_API, EVENT
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False) # e.g. {"recipient": "manager", "template": "LOW_STOCK"}
    sequence_order: Mapped[int] = mapped_column(Integer, default=1)

class WorkflowExecution(AuditBase):
    __tablename__ = "workflow_executions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False)
    workflow_version: Mapped[int] = mapped_column(Integer, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. INVENTORY, INVOICE
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="RUNNING") # RUNNING, COMPLETED, FAILED
    error_message: Mapped[Optional[str]] = mapped_column(Text)
