"""Provisionamento atômico de tenant, membership e schema analítico."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Membership, Tenant

ROLE_EXECUTOR = "nexo_executor"


def schema_name(tenant_id: str) -> str:
    return "t_" + str(UUID(tenant_id)).replace("-", "")


def _sql_literal(value: str) -> str:
    return value.replace("'", "''")


def ensure_analytic_schema(connection, schema: str) -> None:
    if connection.dialect.name != "postgresql":
        return
    quoted = _sql_literal(schema)
    connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{quoted}"'))
    connection.execute(text(f'REVOKE ALL ON SCHEMA "{quoted}" FROM PUBLIC'))


def grant_executor_schema(connection, schema: str) -> None:
    """Concede leitura analítica somente ao schema indicado (publicação futura)."""
    if connection.dialect.name != "postgresql":
        return
    ensure_analytic_schema(connection, schema)
    quoted = _sql_literal(schema)
    connection.execute(text(f'GRANT USAGE ON SCHEMA "{quoted}" TO {ROLE_EXECUTOR}'))
    connection.execute(
        text(
            f'ALTER DEFAULT PRIVILEGES IN SCHEMA "{quoted}" '
            f"GRANT SELECT ON TABLES TO {ROLE_EXECUTOR}"
        )
    )


def provision_tenant(
    db: Session,
    name: str,
    owner_user_id: str,
    *,
    tenant_id: str | None = None,
) -> Tenant:
    """Cria tenant, membership owner e schema analítico numa única transação."""
    tid = tenant_id or str(uuid4())
    schema = schema_name(tid)
    bind = db.get_bind()
    tenant = Tenant(id=tid, name=name, schema_name=schema)
    db.add(tenant)
    db.flush()
    db.add(Membership(tenant_id=tid, user_id=owner_user_id, role="owner"))
    db.flush()
    if bind.dialect.name == "postgresql":
        try:
            ensure_analytic_schema(db.connection(), schema)
        except SQLAlchemyError:
            db.rollback()
            raise
    return tenant
