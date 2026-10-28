from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

def new_id():
    return str(uuid4())

def now():
    return datetime.now(timezone.utc)

class Identity:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Tenant(Identity, Base):
    __tablename__ = "tenants"
    name: Mapped[str] = mapped_column(String(120))
    schema_name: Mapped[str] = mapped_column(String(40), unique=True)

class Membership(Identity, Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id"),)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(16), default="viewer")

class TenantOwned(Identity):
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)

class Source(TenantOwned, Base):
    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("tenant_id", "name"),)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(24), default="draft")
    secret_ref: Mapped[str | None] = mapped_column(String(250), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

class SyncRun(TenantOwned, Base):
    __tablename__ = "sync_runs"
    __table_args__ = (UniqueConstraint("tenant_id", "source_id", "idempotency_key"),)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    idempotency_key: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(24), default="pending")
    summary: Mapped[dict] = mapped_column(JSON, default=dict)

class Dataset(TenantOwned, Base):
    __tablename__ = "datasets"
    __table_args__ = (UniqueConstraint("source_id", "table_name"),)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    table_name: Mapped[str] = mapped_column(String(63))
    version: Mapped[int] = mapped_column(default=1)
    catalog: Mapped[dict] = mapped_column(JSON, default=dict)

class SemanticRule(TenantOwned, Base):
    __tablename__ = "semantic_rules"
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    version: Mapped[int] = mapped_column(default=1)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

class Conversation(TenantOwned, Base):
    __tablename__ = "conversations"
    title: Mapped[str] = mapped_column(String(180))
    user_id: Mapped[str] = mapped_column(String(36))

class Message(TenantOwned, Base):
    __tablename__ = "messages"
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (Index("ix_messages_conversation_created", "conversation_id", "created_at"),)

class QueryRun(TenantOwned, Base):
    __tablename__ = "query_runs"
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24))
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)

class Correction(TenantOwned, Base):
    __tablename__ = "corrections"
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    reason: Mapped[str] = mapped_column(Text)
    proposed_rule: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="pending")

class Dashboard(TenantOwned, Base):
    __tablename__ = "dashboards"
    name: Mapped[str] = mapped_column(String(120))
    spec: Mapped[dict] = mapped_column(JSON, default=dict)

class ReportSchedule(TenantOwned, Base):
    __tablename__ = "report_schedules"
    dashboard_id: Mapped[str] = mapped_column(ForeignKey("dashboards.id", ondelete="CASCADE"))
    timezone: Mapped[str] = mapped_column(String(80), default="America/Sao_Paulo")
    cron: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(default=False)

class Integration(TenantOwned, Base):
    __tablename__ = "integrations"
    provider: Mapped[str] = mapped_column(String(30))
    external_id: Mapped[str] = mapped_column(String(160))
    secret_ref: Mapped[str] = mapped_column(String(250))
    __table_args__ = (UniqueConstraint("provider", "external_id"),)

class WebhookEvent(TenantOwned, Base):
    __tablename__ = "webhook_events"
    provider: Mapped[str] = mapped_column(String(30))
    external_id: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="received")
    __table_args__ = (UniqueConstraint("provider", "external_id"),)

class Subscription(TenantOwned, Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("tenant_id"),)
    provider_id: Mapped[str | None] = mapped_column(String(160), unique=True, nullable=True)
    plan: Mapped[str] = mapped_column(String(30), default="pilot")
    status: Mapped[str] = mapped_column(String(24), default="trial")
    monthly_limit: Mapped[int] = mapped_column(default=1000)

class UsageEvent(TenantOwned, Base):
    __tablename__ = "usage_events"
    kind: Mapped[str] = mapped_column(String(30))
    units: Mapped[int] = mapped_column(default=1)
    __table_args__ = (Index("ix_usage_tenant_date", "tenant_id", "created_at"),)

class AuditEvent(TenantOwned, Base):
    __tablename__ = "audit_events"
    actor_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str] = mapped_column(String(36))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
