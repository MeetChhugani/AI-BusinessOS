import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import AuditBase

class LLMProvider(AuditBase):
    __tablename__ = "ai_llm_providers"

    name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. OpenAI, Anthropic, Gemini
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g. OPENAI
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")

class ModelConfiguration(AuditBase):
    __tablename__ = "ai_model_configurations"

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_llm_providers.id", ondelete="CASCADE"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. gpt-4o, claude-3-5-sonnet
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

class AISession(AuditBase):
    __tablename__ = "ai_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE") # ACTIVE, CLOSED

class AIConversation(AuditBase):
    __tablename__ = "ai_conversations"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    current_goal: Mapped[Optional[str]] = mapped_column(Text)
    completed_tasks: Mapped[Optional[dict]] = mapped_column(JSONB) # e.g. {"tasks": ["Query revenue"]}
    pending_tasks: Mapped[Optional[dict]] = mapped_column(JSONB)
    active_entities: Mapped[Optional[dict]] = mapped_column(JSONB) # e.g. {"customerId": "..."}

class AIMessage(AuditBase):
    __tablename__ = "ai_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False) # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Optional[str]] = mapped_column(String(20)) # HIGH, MEDIUM, LOW

class AgentDefinition(AuditBase):
    __tablename__ = "ai_agent_definitions"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g. FINANCE_AGENT
    capabilities: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    version: Mapped[int] = mapped_column(Integer, default=1)

class AgentExecution(AuditBase):
    __tablename__ = "ai_agent_executions"

    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_agent_definitions.id", ondelete="CASCADE"), nullable=False)
    tool_used: Mapped[Optional[str]] = mapped_column(String(100))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    inputs_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    outputs_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    confidence: Mapped[str] = mapped_column(String(20), default="HIGH") # HIGH, MEDIUM, LOW
    error_message: Mapped[Optional[str]] = mapped_column(Text)

class PromptTemplate(AuditBase):
    __tablename__ = "ai_prompt_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. SUMMARY_PROMPT

class PromptVersion(AuditBase):
    __tablename__ = "ai_prompt_versions"

    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_prompt_templates.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)

class KnowledgeDocument(AuditBase):
    __tablename__ = "ai_knowledge_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    file_metadata_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("file_metadata.id", ondelete="SET NULL"))

class KnowledgeChunk(AuditBase):
    __tablename__ = "ai_knowledge_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    chunk_content: Mapped[str] = mapped_column(Text, nullable=False)

class EmbeddingRecord(AuditBase):
    __tablename__ = "ai_embedding_records"

    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_knowledge_chunks.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    embedding_vector: Mapped[str] = mapped_column(Text, nullable=False) # stored as string representation of floating list

class VectorIndex(AuditBase):
    __tablename__ = "ai_vector_indexes"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    index_type: Mapped[str] = mapped_column(String(50), default="HNSW")

class MemoryRecord(AuditBase):
    __tablename__ = "ai_memory_records"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_type: Mapped[str] = mapped_column(String(30), default="LONG_TERM") # SHORT_TERM, LONG_TERM
    content: Mapped[str] = mapped_column(Text, nullable=False)

class BusinessContext(AuditBase):
    __tablename__ = "ai_business_contexts"

    context_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    context_value: Mapped[str] = mapped_column(Text, nullable=False)

class BusinessEntity(AuditBase):
    __tablename__ = "ai_business_entities"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. Customer, Order
    reference_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

class BusinessRelationship(AuditBase):
    __tablename__ = "ai_business_relationships"

    source_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_business_entities.id", ondelete="CASCADE"), nullable=False)
    target_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_business_entities.id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. Customer_Orders_Order

class ToolDefinition(AuditBase):
    __tablename__ = "ai_tool_definitions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. search_customers
    description: Mapped[str] = mapped_column(Text, nullable=False)
    input_schema: Mapped[dict] = mapped_column(JSONB, nullable=False)
    required_permissions: Mapped[str] = mapped_column(String(255), default="platform.settings.write")
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    retry_policy_max: Mapped[int] = mapped_column(Integer, default=3)

class CopilotPreference(AuditBase):
    __tablename__ = "ai_copilot_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    default_model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_model_configurations.id"))
    theme_preference: Mapped[str] = mapped_column(String(20), default="DARK")

class AIFeedback(AuditBase):
    __tablename__ = "ai_feedback"

    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_messages.id", ondelete="CASCADE"), nullable=False)
    is_positive: Mapped[bool] = mapped_column(Boolean, default=True)
    rating_comment: Mapped[Optional[str]] = mapped_column(Text)

class AIAudit(AuditBase):
    __tablename__ = "ai_audits"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action_performed: Mapped[str] = mapped_column(String(255), nullable=False)
    tokens_consumed: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
