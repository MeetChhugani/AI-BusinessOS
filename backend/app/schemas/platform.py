from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class NotificationLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    message: str
    channel: str
    priority: str
    delivery_status: str
    read_status: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowTriggerCreate(BaseModel):
    trigger_type: str
    event_name: str
    parameters: Optional[dict] = None

class WorkflowConditionCreate(BaseModel):
    operator: str = "AND"
    expression: dict

class WorkflowActionCreate(BaseModel):
    action_type: str
    parameters: dict
    sequence_order: int = 1

class WorkflowDefinitionCreate(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None
    triggers: List[WorkflowTriggerCreate]
    conditions: List[WorkflowConditionCreate]
    actions: List[WorkflowActionCreate]

class WorkflowDefinitionResponse(BaseModel):
    id: UUID
    name: str
    code: str
    version: int
    description: Optional[str]
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditEventResponse(BaseModel):
    id: UUID
    entity_name: str
    entity_id: UUID
    operation: str
    old_value: Optional[str]
    new_value: Optional[str]
    source: str
    user_id: Optional[UUID]
    request_id: Optional[str]
    ip_address: Optional[str]
    browser: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FileMetadataResponse(BaseModel):
    id: UUID
    name: str
    folder_id: Optional[UUID]
    mime_type: str
    file_size_bytes: int
    storage_path: str
    sha256_checksum: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ScheduledJobResponse(BaseModel):
    id: UUID
    name: str
    code: str
    cron_expression: str
    status: str
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

class SystemSettingResponse(BaseModel):
    id: UUID
    key: str
    value: str
    category: str
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class FeatureFlagResponse(BaseModel):
    id: UUID
    name: str
    enabled: bool
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class SearchIndexResponse(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    title: str
    description: Optional[str]
    metadata_json: Optional[dict]
    model_config = ConfigDict(from_attributes=True)

class SystemEventResponse(BaseModel):
    id: UUID
    event_name: str
    correlation_id: UUID
    parent_event_id: Optional[UUID]
    version: int
    payload: dict
    status: str
    duration_ms: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class HealthMetricResponse(BaseModel):
    id: UUID
    api_latency_ms: float
    db_latency_ms: float
    redis_connected: bool
    disk_usage_percent: float
    memory_usage_percent: float
    scheduler_queue_depth: int
    email_queue_depth: int
    workflow_queue_depth: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
