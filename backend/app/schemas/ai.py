from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class AIMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    confidence_score: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AIConversationResponse(BaseModel):
    id: UUID
    session_id: UUID
    title: str
    current_goal: Optional[str]
    completed_tasks: Optional[Dict[str, Any]]
    pending_tasks: Optional[Dict[str, Any]]
    active_entities: Optional[Dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AISessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AIChatRequest(BaseModel):
    conversation_id: UUID
    prompt: str

class AIChatResponse(BaseModel):
    content: str
    confidence: str = "HIGH"
    conversation_id: UUID

class AgentExecutionResponse(BaseModel):
    id: UUID
    agent_id: UUID
    tool_used: Optional[str]
    duration_ms: int
    inputs_payload: Optional[Dict[str, Any]]
    outputs_payload: Optional[Dict[str, Any]]
    confidence: str
    error_message: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ToolDefinitionResponse(BaseModel):
    id: UUID
    name: str
    description: str
    input_schema: Dict[str, Any]
    required_permissions: str
    timeout_seconds: int
    model_config = ConfigDict(from_attributes=True)
