from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, RoleChecker
from app.database.session import get_db_session
from app.models.workflow import WorkflowDefinition, WorkflowTrigger, WorkflowCondition, WorkflowAction
from app.schemas.platform import WorkflowDefinitionCreate, WorkflowDefinitionResponse

router = APIRouter(prefix="/workflows", tags=["Workflow Automation Engine"])

@router.get("", response_model=List[WorkflowDefinitionResponse], summary="List workflow definitions")
async def list_workflows(
    db: AsyncSession = Depends(get_db_session)
) -> List[WorkflowDefinition]:
    query = select(WorkflowDefinition).where(WorkflowDefinition.deleted_at.is_(None))
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=WorkflowDefinitionResponse, status_code=201, summary="Configure new automation rule")
async def create_workflow(
    body: WorkflowDefinitionCreate,
    current_user = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"])),
    db: AsyncSession = Depends(get_db_session)
) -> WorkflowDefinition:
    # Auto-increment versioning if code already exists
    version = 1
    exist_q = select(WorkflowDefinition).where(WorkflowDefinition.code == body.code).order_by(WorkflowDefinition.version.desc())
    exist_res = await db.execute(exist_q)
    latest = exist_res.scalars().first()
    if latest:
        version = latest.version + 1

    wf = WorkflowDefinition(
        name=body.name,
        code=body.code,
        version=version,
        description=body.description,
        status="ACTIVE"
    )
    db.add(wf)
    await db.flush()

    for trig in body.triggers:
        db.add(
            WorkflowTrigger(
                workflow_id=wf.id,
                trigger_type=trig.trigger_type,
                event_name=trig.event_name,
                parameters=trig.parameters
            )
        )

    for cond in body.conditions:
        db.add(
            WorkflowCondition(
                workflow_id=wf.id,
                operator=cond.operator,
                expression=cond.expression
            )
        )

    for act in body.actions:
        db.add(
            WorkflowAction(
                workflow_id=wf.id,
                action_type=act.action_type,
                parameters=act.parameters,
                sequence_order=act.sequence_order
            )
        )

    await db.commit()
    await db.refresh(wf)
    return wf
