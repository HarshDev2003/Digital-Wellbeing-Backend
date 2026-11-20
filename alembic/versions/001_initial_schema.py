"""Initial database schema migration creating all 17 tables for Digital Wellbeing.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-21 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 2. refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 3. user_consents
    op.create_table(
        "user_consents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("consent_type", sa.String(64), nullable=False),
        sa.Column("policy_version", sa.String(32), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 4. devices
    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_identifier", sa.String(128), nullable=False),
        sa.Column("platform", sa.String(16), nullable=False),
        sa.Column("device_model", sa.String(128), nullable=False),
        sa.Column("os_version", sa.String(32), nullable=False),
        sa.Column("app_version", sa.String(32), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "device_identifier", name="uq_user_device_identifier"),
    )

    # 5. device_capabilities
    op.create_table(
        "device_capabilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("supports_network_tracking", sa.Boolean(), nullable=False),
        sa.Column("supports_app_shielding", sa.Boolean(), nullable=False),
        sa.Column("has_usage_permission", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("has_screen_time_permission", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 6. app_categories
    op.create_table(
        "app_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("color_hex", sa.String(7), nullable=False),
    )

    # 7. installed_apps
    op.create_table(
        "installed_apps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("app_name", sa.String(255), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("app_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("device_id", "package_name", name="uq_device_package_name"),
    )

    # 8. app_usage_events
    op.create_table(
        "app_usage_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("device_id", "event_uuid", name="uq_app_event_device_uuid"),
    )
    op.create_index("idx_app_events_device_time", "app_usage_events", ["device_id", "start_time"])
    op.create_index("idx_app_events_package", "app_usage_events", ["package_name"])

    # 9. screen_activity_events
    op.create_table(
        "screen_activity_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("device_id", "event_uuid", name="uq_screen_event_device_uuid"),
    )
    op.create_index("idx_screen_events_device_time", "screen_activity_events", ["device_id", "timestamp"])

    # 10. network_usage_events
    op.create_table(
        "network_usage_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("wifi_bytes_rx", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("wifi_bytes_tx", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("mobile_bytes_rx", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("mobile_bytes_tx", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("calendar_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("device_id", "event_uuid", name="uq_network_event_device_uuid"),
    )
    op.create_index("idx_network_device_date", "network_usage_events", ["device_id", "calendar_date"])

    # 11. daily_usage_summaries
    op.create_table(
        "daily_usage_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("calendar_date", sa.Date(), nullable=False),
        sa.Column("total_screen_time_seconds", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_unlocks", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_sessions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "device_id", "calendar_date", name="uq_daily_summary_user_device_date"),
    )
    op.create_index("idx_daily_summaries_user_date", "daily_usage_summaries", ["user_id", "calendar_date"])

    # 12. app_daily_summaries
    op.create_table(
        "app_daily_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("daily_summary_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("daily_usage_summaries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("total_foreground_seconds", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("session_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("daily_summary_id", "package_name", name="uq_app_daily_summary_pkg"),
    )

    # 13. usage_goals
    op.create_table(
        "usage_goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("app_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("max_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 14. app_limits
    op.create_table(
        "app_limits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("max_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "package_name", name="uq_user_app_limit_pkg"),
    )

    # 15. app_limit_violations
    op.create_table(
        "app_limit_violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("package_name", sa.String(255), nullable=False),
        sa.Column("violation_date", sa.Date(), nullable=False),
        sa.Column("actual_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("limit_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 16. user_insights
    op.create_table(
        "user_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("insight_type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("structured_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("wellbeing_score", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 17. app_tasks
    op.create_table(
        "app_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_type", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(16), nullable=False, server_default="PENDING"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_app_tasks_worker", "app_tasks", ["status", "scheduled_at"])


def downgrade() -> None:
    op.drop_table("app_tasks")
    op.drop_table("user_insights")
    op.drop_table("app_limit_violations")
    op.drop_table("app_limits")
    op.drop_table("usage_goals")
    op.drop_table("app_daily_summaries")
    op.drop_table("daily_usage_summaries")
    op.drop_table("network_usage_events")
    op.drop_table("screen_activity_events")
    op.drop_table("app_usage_events")
    op.drop_table("installed_apps")
    op.drop_table("app_categories")
    op.drop_table("device_capabilities")
    op.drop_table("devices")
    op.drop_table("user_consents")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
