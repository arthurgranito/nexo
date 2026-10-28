"""Acesso ao plano de controle sempre escopado por tenant e contexto RLS."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import apply_session_context
from app.models import (
    Conversation,
    Correction,
    Dashboard,
    Membership,
    Message,
    Source,
    Tenant,
)


class Repositories:
    def __init__(self, db: Session, *, tenant_id: str | None, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        apply_session_context(db, tenant_id=tenant_id, user_id=user_id)

    def memberships_for_user(self) -> list[Membership]:
        return list(self.db.scalars(select(Membership).where(Membership.user_id == self.user_id)))

    def tenant(self, tenant_id: str) -> Tenant | None:
        return self.db.get(Tenant, tenant_id)

    def sources(self, *, offset: int = 0, limit: int = 25) -> list[Source]:
        assert self.tenant_id is not None
        return list(
            self.db.scalars(
                select(Source)
                .where(Source.tenant_id == self.tenant_id)
                .order_by(Source.created_at, Source.id)
                .offset(offset)
                .limit(limit)
            )
        )

    def add_source(self, source: Source) -> Source:
        assert self.tenant_id is not None
        if source.tenant_id != self.tenant_id:
            raise ValueError("tenant_id inconsistente")
        self.db.add(source)
        return source

    def assistant_message(self, message_id: str) -> Message | None:
        assert self.tenant_id is not None
        return self.db.scalar(
            select(Message).where(
                Message.id == message_id,
                Message.tenant_id == self.tenant_id,
                Message.role == "assistant",
            )
        )

    def add_correction(self, correction: Correction) -> Correction:
        assert self.tenant_id is not None
        if correction.tenant_id != self.tenant_id:
            raise ValueError("tenant_id inconsistente")
        self.db.add(correction)
        return correction

    def dashboards(self, *, offset: int = 0, limit: int = 25) -> list[Dashboard]:
        assert self.tenant_id is not None
        return list(
            self.db.scalars(
                select(Dashboard)
                .where(Dashboard.tenant_id == self.tenant_id)
                .order_by(Dashboard.created_at, Dashboard.id)
                .offset(offset)
                .limit(limit)
            )
        )

    def add_dashboard(self, dashboard: Dashboard) -> Dashboard:
        assert self.tenant_id is not None
        if dashboard.tenant_id != self.tenant_id:
            raise ValueError("tenant_id inconsistente")
        self.db.add(dashboard)
        return dashboard

    def add_conversation(self, conversation: Conversation) -> Conversation:
        assert self.tenant_id is not None
        if conversation.tenant_id != self.tenant_id:
            raise ValueError("tenant_id inconsistente")
        self.db.add(conversation)
        return conversation

    def add_message(self, message: Message) -> Message:
        assert self.tenant_id is not None
        if message.tenant_id != self.tenant_id:
            raise ValueError("tenant_id inconsistente")
        self.db.add(message)
        return message

    def count_sources(self) -> int:
        assert self.tenant_id is not None
        from sqlalchemy import func

        return self.db.scalar(
            select(func.count()).select_from(Source).where(Source.tenant_id == self.tenant_id)
        ) or 0
