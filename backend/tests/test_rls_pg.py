"""RLS fail-closed no plano de controle via role nexo_api."""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db import apply_session_context
from app.models import Source
from app.tenancy import provision_tenant

def _needs_pg() -> bool:
    owner = os.environ.get("DATABASE_URL", "")
    api = os.environ.get("POSTGRES_TEST_URL") or os.environ.get("DATABASE_API_URL", "")
    return owner.startswith("postgresql") and api.startswith("postgresql")


def _api_url() -> str:
    return os.environ.get("POSTGRES_TEST_URL") or os.environ["DATABASE_API_URL"]


pytestmark = pytest.mark.skipif(not _needs_pg(), reason="PostgreSQL de teste não configurado")


@pytest.fixture
def two_tenants():
    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    factory = sessionmaker(engine, expire_on_commit=False)
    user = str(uuid.uuid4())
    t_a = str(uuid.uuid4())
    t_b = str(uuid.uuid4())
    with factory.begin() as db:
        provision_tenant(db, "Tenant A", user, tenant_id=t_a)
        provision_tenant(db, "Tenant B", user, tenant_id=t_b)
        apply_session_context(db, tenant_id=t_a, user_id=user)
        db.add(Source(tenant_id=t_a, name="Fonte A", kind="csv"))
        apply_session_context(db, tenant_id=t_b, user_id=user)
        db.add(Source(tenant_id=t_b, name="Fonte B", kind="csv"))
    engine.dispose()
    return user, t_a, t_b


def test_api_role_cannot_read_other_tenant(two_tenants):
    user, t_a, t_b = two_tenants
    api = create_engine(_api_url(), pool_pre_ping=True)
    factory = sessionmaker(api, expire_on_commit=False)
    with factory() as db:
        apply_session_context(db, tenant_id=t_a, user_id=user)
        rows = db.scalars(select(Source).where(Source.tenant_id == t_a)).all()
        assert len(rows) == 1
        assert rows[0].name == "Fonte A"
    with factory() as db:
        apply_session_context(db, tenant_id=t_b, user_id=user)
        cross = db.scalars(select(Source).where(Source.tenant_id == t_a)).all()
        assert cross == []
    api.dispose()


def test_api_role_rejects_cross_tenant_insert(two_tenants):
    user, t_a, t_b = two_tenants
    api = create_engine(_api_url(), pool_pre_ping=True)
    factory = sessionmaker(api, expire_on_commit=False)
    with factory() as db:
        apply_session_context(db, tenant_id=t_a, user_id=user)
        db.add(Source(tenant_id=t_b, name="Invasão", kind="csv"))
        with pytest.raises(Exception):
            db.commit()
        db.rollback()
    api.dispose()

