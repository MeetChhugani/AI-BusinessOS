from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.exceptions.custom_exceptions import EntityNotFoundException
from app.models.ai import AISession, AIConversation, AgentExecution, ToolDefinition
from app.services.ai_service import AgentOrchestrator, GuardrailService
from app.schemas.ai import (
    AISessionResponse, AIConversationResponse, AIChatRequest, AIChatResponse,
    AgentExecutionResponse, ToolDefinitionResponse
)

router = APIRouter(prefix="/ai", tags=["Enterprise AI Platform"])

@router.post("/sessions", response_model=AISessionResponse, status_code=201, summary="Create new AI session context")
async def create_session(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> AISession:
    sess = AISession(user_id=current_user.id, status="ACTIVE")
    db.add(sess)
    await db.commit()
    await db.refresh(sess)
    return sess

@router.post("/chat", response_model=AIChatResponse, summary="Send message to Business Copilot two-tier pipeline")
async def chat_copilot(
    body: AIChatRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Prompt injection check
    GuardrailService.inspect_prompt(body.prompt)

    # Resolve active conversation or create one
    conv_q = select(AIConversation).where(AIConversation.id == body.conversation_id)
    conv_res = await db.execute(conv_q)
    conv = conv_res.scalars().first()
    if not conv:
        # Resolve any active session for the user
        sess_q = select(AISession).where(AISession.user_id == current_user.id).order_by(AISession.created_at.desc())
        sess_res = await db.execute(sess_q)
        sess = sess_res.scalars().first()
        if not sess:
            sess = AISession(user_id=current_user.id, status="ACTIVE")
            db.add(sess)
            await db.flush()
        
        conv = AIConversation(session_id=sess.id, title="Automatic Chat Session")
        db.add(conv)
        await db.flush()
        body.conversation_id = conv.id

    ans = await AgentOrchestrator.run_planner_supervisor_pipeline(
        db,
        conversation_id=body.conversation_id,
        user_prompt=body.prompt,
        user_role=current_user.role
    )
    return {
        "content": ans,
        "confidence": "HIGH",
        "conversation_id": body.conversation_id
    }

@router.get("/agents/executions", response_model=List[AgentExecutionResponse], summary="Retrieve dynamic agent execution audits trace")
async def list_agent_traces(
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
) -> List[AgentExecution]:
    query = select(AgentExecution).order_by(AgentExecution.created_at.desc())
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/tools", response_model=List[ToolDefinitionResponse], summary="List dynamically registered ERP tools")
async def list_registered_tools(
    db: AsyncSession = Depends(get_db_session)
) -> List[ToolDefinition]:
    query = select(ToolDefinition).where(ToolDefinition.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())
