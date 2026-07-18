import uuid
import hashlib
import os
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.custom_exceptions import ValidationException, EntityNotFoundException
from app.logging.config import logger

from app.models.notifications import NotificationTemplate, NotificationPreference, NotificationLog
from app.models.workflow import WorkflowDefinition, WorkflowTrigger, WorkflowCondition, WorkflowAction, WorkflowExecution
from app.models.audit import AuditEvent, AuditChange
from app.models.storage import FileFolder, FileMetadata
from app.models.scheduler import ScheduledJob, JobExecution
from app.models.settings import SystemSetting, FeatureFlag
from app.models.search import SearchIndex
from app.models.events import SystemEvent
from app.models.health import HealthMetric

# Central Permission Registry
PERMISSION_REGISTRY = [
    "hcm.employee.read", "hcm.employee.write", "hcm.salary.write",
    "inventory.warehouse.read", "inventory.warehouse.write", "inventory.stock.adjust",
    "crm.customer.read", "crm.customer.write", "crm.order.approve",
    "finance.ledger.read", "finance.ledger.write", "finance.post",
    "platform.settings.write", "platform.workflows.write", "platform.features.toggle"
]

class NotificationService:
    @staticmethod
    async def log_notification(
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        message: str,
        channel: str = "IN_APP",
        priority: str = "NORMAL"
    ) -> NotificationLog:
        # Check preference
        pref_q = select(NotificationPreference).where(
            and_(NotificationPreference.user_id == user_id, NotificationPreference.category == "GENERAL")
        )
        pref_res = await db.execute(pref_q)
        pref = pref_res.scalars().first()
        
        if pref:
            if channel == "IN_APP" and not pref.in_app_enabled:
                raise ValidationException("In-App notifications disabled by preference settings")
            if channel == "EMAIL" and not pref.email_enabled:
                raise ValidationException("Email notifications disabled by preference settings")

        log = NotificationLog(
            user_id=user_id,
            title=title,
            message=message,
            channel=channel,
            priority=priority,
            delivery_status="SENT"
        )
        db.add(log)
        await db.commit()
        logger.info("notification_dispatched", user_id=str(user_id), channel=channel)
        return log

class EmailService:
    @staticmethod
    async def send_templated_email(
        db: AsyncSession,
        to_email: str,
        template_code: str,
        variables: Dict[str, Any]
    ) -> bool:
        temp_q = select(NotificationTemplate).where(NotificationTemplate.code == template_code)
        temp_res = await db.execute(temp_q)
        template = temp_res.scalars().first()
        if not template:
            raise EntityNotFoundException("Email template not found")

        # Compile templates
        subject = template.subject_template
        body = template.body_template
        for k, v in variables.items():
            subject = subject.replace(f"{{{{{k}}}}}", str(v))
            body = body.replace(f"{{{{{k}}}}}", str(v))

        # Real ERP systems queue emails for background transmission
        logger.info("queued_templated_email", to=to_email, subject=subject)
        return True

class FileStorageService:
    @staticmethod
    async def upload_file(
        db: AsyncSession,
        name: str,
        content: bytes,
        mime_type: str,
        uploaded_by_id: Optional[uuid.UUID] = None
    ) -> FileMetadata:
        # Calculate SHA256 checksum to prevent duplicate storage
        sha256 = hashlib.sha256(content).hexdigest()
        
        # Duplicate detection check
        dup_q = select(FileMetadata).where(FileMetadata.sha256_checksum == sha256)
        dup_res = await db.execute(dup_q)
        dup = dup_res.scalars().first()
        if dup:
            logger.info("duplicate_file_detected_reusing_metadata", sha256=sha256)
            return dup

        # Local storage destination path
        storage_dir = "C:/Users/meetc/Desktop/AI BusinessOS/storage/"
        os.makedirs(storage_dir, exist_ok=True)
        local_path = os.path.join(storage_dir, f"{uuid.uuid4()}_{name}")
        
        with open(local_path, "wb") as f:
            f.write(content)

        meta = FileMetadata(
            name=name,
            mime_type=mime_type,
            file_size_bytes=len(content),
            storage_path=local_path,
            sha256_checksum=sha256,
            uploaded_by_id=uploaded_by_id
        )
        db.add(meta)
        await db.commit()
        await db.refresh(meta)
        logger.info("file_stored_successfully", sha256=sha256)
        return meta

class WorkflowEngine:
    @staticmethod
    async def execute_event_rules(
        db: AsyncSession,
        event_name: str,
        entity_type: str,
        entity_id: uuid.UUID,
        payload: Dict[str, Any]
    ) -> None:
        # Fetch active workflow definitions matching trigger event
        wf_q = select(WorkflowDefinition).where(
            and_(
                WorkflowDefinition.status == "ACTIVE"
            )
        ).join(WorkflowTrigger, WorkflowTrigger.workflow_id == WorkflowDefinition.id).where(
            WorkflowTrigger.event_name == event_name
        )
        wf_res = await db.execute(wf_q)
        workflows = wf_res.scalars().all()

        for wf in workflows:
            # Check conditions (Trigger-Condition-Action model validation)
            cond_q = select(WorkflowCondition).where(WorkflowCondition.workflow_id == wf.id)
            cond_res = await db.execute(cond_q)
            conditions = cond_res.scalars().all()

            conditions_met = True
            for cond in conditions:
                expr = cond.expression
                field_val = payload.get(expr.get("field"))
                expected_val = expr.get("value")
                op = expr.get("op")

                if op == "LT" and not (field_val is not None and field_val < expected_val):
                    conditions_met = False
                elif op == "GT" and not (field_val is not None and field_val > expected_val):
                    conditions_met = False
                elif op == "EQ" and not (field_val == expected_val):
                    conditions_met = False

            if conditions_met:
                # Log execution state machine
                exec_log = WorkflowExecution(
                    workflow_id=wf.id,
                    workflow_version=wf.version,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    status="COMPLETED"
                )
                db.add(exec_log)

                # Process Actions
                act_q = select(WorkflowAction).where(WorkflowAction.workflow_id == wf.id).order_by(WorkflowAction.sequence_order)
                act_res = await db.execute(act_q)
                actions = act_res.scalars().all()

                for act in actions:
                    if act.action_type == "NOTIFY":
                        # Send in-app notification to target user
                        user_id = act.parameters.get("user_id")
                        if user_id:
                            await NotificationService.log_notification(
                                db,
                                uuid.UUID(user_id),
                                "Automated Workflow alert",
                                act.parameters.get("message", "Trigger event triggered action")
                            )

        await db.commit()

class SearchService:
    @staticmethod
    async def index_entity(
        db: AsyncSession,
        entity_type: str,
        entity_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> SearchIndex:
        index = SearchIndex(
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            description=description,
            keywords=keywords,
            metadata_json=metadata
        )
        db.add(index)
        await db.commit()
        return index

    @staticmethod
    async def search_query(db: AsyncSession, term: str) -> List[SearchIndex]:
        # Generic query search across title description and keywords
        query = select(SearchIndex).where(
            or_(
                SearchIndex.title.icontains(term),
                SearchIndex.description.icontains(term),
                SearchIndex.keywords.icontains(term)
            )
        )
        res = await db.execute(query)
        return list(res.scalars().all())

class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        entity_name: str,
        entity_id: uuid.UUID,
        operation: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        source: str = "API",
        user_id: Optional[uuid.UUID] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        browser: Optional[str] = None
    ) -> AuditEvent:
        event = AuditEvent(
            entity_name=entity_name,
            entity_id=entity_id,
            operation=operation,
            old_value=old_value,
            new_value=new_value,
            source=source,
            user_id=user_id,
            request_id=request_id,
            ip_address=ip_address,
            browser=browser
        )
        db.add(event)
        await db.commit()
        return event

class FeatureFlagService:
    @staticmethod
    async def is_enabled(db: AsyncSession, flag_name: str) -> bool:
        q = select(FeatureFlag).where(FeatureFlag.name == flag_name)
        res = await db.execute(q)
        flag = res.scalars().first()
        return flag.enabled if flag else False
