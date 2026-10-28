"""Isolamento de schema analítico e provisionamento (PostgreSQL real)."""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models import Tenant
from app.tenancy import ROLE_EXECUTOR, provision_tenant, schema_name


def _needs_pg() -> bool:
    owner = os.environ.get("DATABASE_URL", "")
    executor = os.environ.get("DATABASE_EXECUTOR_URL", "")
    return owner.startswith("postgresql") and executor.startswith("postgresql")


pytestmark = pytest.mark.skipif(not _needs_pg(), reason="PostgreSQL de teste não configurado")


@pytest.fixture
def owner_session():
    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory.begin() as session:
        yield session
    engine.dispose()


def test_provision_creates_schema_and_membership(owner_session):
    user = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    tenant = provision_tenant(owner_session, "Org Teste", user, tenant_id=tenant_id)
    owner_session.flush()
    schema = schema_name(tenant_id)
    assert tenant.schema_name == schema
    row = owner_session.execute(
        text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :s"),
        {"s": schema},
    ).first()
    assert row is not None


def test_executor_cannot_read_neighbor_schema():
    owner_url = os.environ["DATABASE_URL"]
    executor_url = os.environ["DATABASE_EXECUTOR_URL"]
    engine = create_engine(owner_url, pool_pre_ping=True)
    factory = sessionmaker(engine, expire_on_commit=False)
    user = str(uuid.uuid4())
    t1 = str(uuid.uuid4())
    t2 = str(uuid.uuid4())
    s1 = schema_name(t1)
    s2 = schema_name(t2)
    with factory.begin() as owner_session:
        provision_tenant(owner_session, "Um", user, tenant_id=t1)
        provision_tenant(owner_session, "Dois", user, tenant_id=t2)
        owner_session.execute(text(f'CREATE TABLE "{s1}".secret (id int)'))
        owner_session.execute(text(f'INSERT INTO "{s1}".secret VALUES (1)'))
        owner_session.execute(text(f'CREATE TABLE "{s2}".other (id int)'))
        owner_session.execute(text(f'GRANT USAGE ON SCHEMA "{s1}" TO {ROLE_EXECUTOR}'))
        owner_session.execute(text(f'GRANT SELECT ON TABLE "{s1}".secret TO {ROLE_EXECUTOR}'))
    exec_engine = create_engine(executor_url, pool_pre_ping=True)
    with exec_engine.connect() as conn:
        allowed = conn.execute(text(f'SELECT id FROM "{s1}".secret')).scalar()
        assert allowed == 1
        with pytest.raises(Exception):
            conn.execute(text(f'SELECT id FROM "{s2}".other'))
    exec_engine.dispose()
    engine.dispose()


def test_provision_rollback_on_duplicate_schema(owner_session):
    user = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    provision_tenant(owner_session, "Primeira", user, tenant_id=tenant_id)
    owner_session.flush()
    dup = Tenant(id=str(uuid.uuid4()), name="Dup", schema_name=schema_name(tenant_id))
    owner_session.add(dup)
    with pytest.raises(Exception):
        owner_session.flush()
    owner_session.rollback()
