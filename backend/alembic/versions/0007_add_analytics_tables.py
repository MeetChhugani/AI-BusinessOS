"""add analytics tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-19 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: Union[str, None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. analytics_dashboards
    op.create_table(
        'analytics_dashboards',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('allowed_roles', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 2. analytics_dashboard_widgets
    op.create_table(
        'analytics_dashboard_widgets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('dashboard_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('widget_type', sa.String(length=50), nullable=False),
        sa.Column('size_x', sa.Integer(), nullable=False),
        sa.Column('size_y', sa.Integer(), nullable=False),
        sa.Column('position_x', sa.Integer(), nullable=False),
        sa.Column('position_y', sa.Integer(), nullable=False),
        sa.Column('query_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dashboard_id'], ['analytics_dashboards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. analytics_saved_dashboards
    op.create_table(
        'analytics_saved_dashboards',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('dashboard_id', sa.UUID(), nullable=False),
        sa.Column('layout_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dashboard_id'], ['analytics_dashboards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. analytics_visualization_templates
    op.create_table(
        'analytics_visualization_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('chart_library', sa.String(length=50), nullable=False),
        sa.Column('default_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. analytics_business_metrics
    op.create_table(
        'analytics_business_metrics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('formula', sa.Text(), nullable=False),
        sa.Column('dependencies_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('cache_refresh_rate', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 6. analytics_business_dimensions
    op.create_table(
        'analytics_business_dimensions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('table_reference', sa.String(length=100), nullable=False),
        sa.Column('field_reference', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 7. analytics_metric_definitions
    op.create_table(
        'analytics_metric_definitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('metric_id', sa.UUID(), nullable=False),
        sa.Column('aggregation_type', sa.String(length=30), nullable=False),
        sa.Column('filters_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['metric_id'], ['analytics_business_metrics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. analytics_metric_snapshots
    op.create_table(
        'analytics_metric_snapshots',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('metric_id', sa.UUID(), nullable=False),
        sa.Column('snapshot_value', sa.Float(), nullable=False),
        sa.Column('dimensions_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['metric_id'], ['analytics_business_metrics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. analytics_forecast_models
    op.create_table(
        'analytics_forecast_models',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('metric_code', sa.String(length=100), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. analytics_forecast_results
    op.create_table(
        'analytics_forecast_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('model_id', sa.UUID(), nullable=False),
        sa.Column('target_date', sa.DateTime(), nullable=False),
        sa.Column('forecasted_value', sa.Float(), nullable=False),
        sa.Column('confidence_lower', sa.Float(), nullable=True),
        sa.Column('confidence_upper', sa.Float(), nullable=True),
        sa.Column('metadata_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['model_id'], ['analytics_forecast_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. analytics_report_definitions
    op.create_table(
        'analytics_report_definitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('columns_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('filters_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('groupings_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. analytics_report_executions
    op.create_table(
        'analytics_report_executions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_id', sa.UUID(), nullable=False),
        sa.Column('run_by_id', sa.UUID(), nullable=False),
        sa.Column('execution_time_ms', sa.Integer(), nullable=False),
        sa.Column('results_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['analytics_report_definitions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. analytics_scheduled_reports
    op.create_table(
        'analytics_scheduled_reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_id', sa.UUID(), nullable=False),
        sa.Column('frequency', sa.String(length=30), nullable=False),
        sa.Column('recipient_emails', sa.Text(), nullable=False),
        sa.Column('export_format', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['analytics_report_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. analytics_drilldown_configurations
    op.create_table(
        'analytics_drilldown_configurations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('hierarchy_path', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. analytics_alert_rules
    op.create_table(
        'analytics_alert_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('metric_code', sa.String(length=100), nullable=False),
        sa.Column('operator', sa.String(length=20), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 16. analytics_alert_executions
    op.create_table(
        'analytics_alert_executions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('rule_id', sa.UUID(), nullable=False),
        sa.Column('triggered_value', sa.Float(), nullable=False),
        sa.Column('workflow_execution_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['analytics_alert_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. analytics_data_exports
    op.create_table(
        'analytics_data_exports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('export_type', sa.String(length=30), nullable=False),
        sa.Column('file_metadata_id', sa.UUID(), nullable=True),
        sa.Column('triggered_by_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['file_metadata_id'], ['file_metadata.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['triggered_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. analytics_kpi_definitions
    op.create_table(
        'analytics_kpi_definitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('metric_code', sa.String(length=100), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('threshold_yellow', sa.Float(), nullable=False),
        sa.Column('threshold_red', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('metric_code')
    )

    # 19. analytics_kpi_values
    op.create_table(
        'analytics_kpi_values',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('kpi_id', sa.UUID(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('status_indicator', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['kpi_id'], ['analytics_kpi_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('analytics_kpi_values')
    op.drop_table('analytics_kpi_definitions')
    op.drop_table('analytics_data_exports')
    op.drop_table('analytics_alert_executions')
    op.drop_table('analytics_alert_rules')
    op.drop_table('analytics_drilldown_configurations')
    op.drop_table('analytics_scheduled_reports')
    op.drop_table('analytics_report_executions')
    op.drop_table('analytics_report_definitions')
    op.drop_table('analytics_forecast_results')
    op.drop_table('analytics_forecast_models')
    op.drop_table('analytics_metric_snapshots')
    op.drop_table('analytics_metric_definitions')
    op.drop_table('analytics_business_dimensions')
    op.drop_table('analytics_business_metrics')
    op.drop_table('analytics_visualization_templates')
    op.drop_table('analytics_saved_dashboards')
    op.drop_table('analytics_dashboard_widgets')
    op.drop_table('analytics_dashboards')
