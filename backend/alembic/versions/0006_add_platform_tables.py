"""add platform tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-19 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0006'
down_revision: Union[str, None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. notification_templates
    op.create_table(
        'notification_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('subject_template', sa.String(length=255), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('channels', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 2. notification_preferences
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('email_enabled', sa.Boolean(), nullable=False),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False),
        sa.Column('sms_enabled', sa.Boolean(), nullable=False),
        sa.Column('whatsapp_enabled', sa.Boolean(), nullable=False),
        sa.Column('push_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. notification_logs
    op.create_table(
        'notification_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('delivery_status', sa.String(length=30), nullable=False),
        sa.Column('read_status', sa.Boolean(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. workflow_definitions
    op.create_table(
        'workflow_definitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. workflow_triggers
    op.create_table(
        'workflow_triggers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workflow_id', sa.UUID(), nullable=False),
        sa.Column('trigger_type', sa.String(length=100), nullable=False),
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. workflow_conditions
    op.create_table(
        'workflow_conditions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workflow_id', sa.UUID(), nullable=False),
        sa.Column('operator', sa.String(length=20), nullable=False),
        sa.Column('expression', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. workflow_actions
    op.create_table(
        'workflow_actions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workflow_id', sa.UUID(), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. workflow_executions
    op.create_table(
        'workflow_executions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workflow_id', sa.UUID(), nullable=False),
        sa.Column('workflow_version', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. audit_events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_name', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('operation', sa.String(length=50), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('browser', sa.String(length=255), nullable=True),
        sa.Column('reason', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. audit_changes
    op.create_table(
        'audit_changes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('audit_event_id', sa.UUID(), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['audit_event_id'], ['audit_events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. file_folders
    op.create_table(
        'file_folders',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('path', sa.String(length=512), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['file_folders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. file_metadata
    op.create_table(
        'file_metadata',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('folder_id', sa.UUID(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=1024), nullable=False),
        sa.Column('sha256_checksum', sa.String(length=64), nullable=False),
        sa.Column('uploaded_by_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['folder_id'], ['file_folders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. scheduled_jobs
    op.create_table(
        'scheduled_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=False),
        sa.Column('backoff_seconds', sa.Integer(), nullable=False),
        sa.Column('dlq_flag', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 14. job_executions
    op.create_table(
        'job_executions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['scheduled_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. system_settings
    op.create_table(
        'system_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)

    # 16. feature_flags
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('rules', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feature_flags_name'), 'feature_flags', ['name'], unique=True)

    # 17. search_indexes
    op.create_table(
        'search_indexes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_indexes_entity_type'), 'search_indexes', ['entity_type'], unique=False)
    op.create_index(op.f('ix_search_indexes_entity_id'), 'search_indexes', ['entity_id'], unique=False)

    # 18. system_events
    op.create_table(
        'system_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('correlation_id', sa.UUID(), nullable=False),
        sa.Column('parent_event_id', sa.UUID(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_events_correlation_id'), 'system_events', ['correlation_id'], unique=False)

    # 19. health_metrics
    op.create_table(
        'health_metrics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('api_latency_ms', sa.Float(), nullable=False),
        sa.Column('db_latency_ms', sa.Float(), nullable=False),
        sa.Column('redis_connected', sa.Boolean(), nullable=False),
        sa.Column('disk_usage_percent', sa.Float(), nullable=False),
        sa.Column('memory_usage_percent', sa.Float(), nullable=False),
        sa.Column('scheduler_queue_depth', sa.Integer(), nullable=False),
        sa.Column('email_queue_depth', sa.Integer(), nullable=False),
        sa.Column('workflow_queue_depth', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('health_metrics')
    op.drop_table('system_events')
    op.drop_table('search_indexes')
    op.drop_table('feature_flags')
    op.drop_table('system_settings')
    op.drop_table('job_executions')
    op.drop_table('scheduled_jobs')
    op.drop_table('file_metadata')
    op.drop_table('file_folders')
    op.drop_table('audit_changes')
    op.drop_table('audit_events')
    op.drop_table('workflow_executions')
    op.drop_table('workflow_actions')
    op.drop_table('workflow_conditions')
    op.drop_table('workflow_triggers')
    op.drop_table('workflow_definitions')
    op.drop_table('notification_logs')
    op.drop_table('notification_preferences')
    op.drop_table('notification_templates')
