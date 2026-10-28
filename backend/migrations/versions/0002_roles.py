"""PostgreSQL roles: migrator, API (RLS) e executor analítico read-only."""
from __future__ import annotations

import os

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

ROLE_MIGRATOR = "nexo_migrator"
ROLE_API = "nexo_api"
ROLE_EXECUTOR = "nexo_executor"


def _pg() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _q(value: str) -> str:
    return value.replace("'", "''")


def _ensure_role(name: str, password: str) -> None:
    pw = _q(password)
    op.execute(
        f"""
        DO $$ BEGIN
          CREATE ROLE {name} LOGIN PASSWORD '{pw}' NOSUPERUSER NOCREATEDB NOCREATEROLE;
        EXCEPTION WHEN duplicate_object THEN
          ALTER ROLE {name} PASSWORD '{pw}';
        END $$;
        """
    )


def upgrade():
    if not _pg():
        return
    migrator_pw = os.environ.get("NEXO_MIGRATOR_PASSWORD", "nexo_migrator_local_dev_only")
    api_pw = os.environ.get("NEXO_API_PASSWORD", "nexo_api_local_dev_only")
    executor_pw = os.environ.get("NEXO_EXECUTOR_PASSWORD", "nexo_executor_local_dev_only")
    _ensure_role(ROLE_MIGRATOR, migrator_pw)
    _ensure_role(ROLE_API, api_pw)
    _ensure_role(ROLE_EXECUTOR, executor_pw)
    op.execute(f"GRANT CONNECT ON DATABASE nexo TO {ROLE_MIGRATOR}, {ROLE_API}, {ROLE_EXECUTOR}")
    op.execute(f"GRANT USAGE, CREATE ON SCHEMA public TO {ROLE_MIGRATOR}")
    op.execute(f"GRANT USAGE ON SCHEMA public TO {ROLE_API}, {ROLE_EXECUTOR}")
    op.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {ROLE_API}"
    )
    op.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {ROLE_API}")
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {ROLE_API}"
    )
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT USAGE, SELECT ON SEQUENCES TO {ROLE_API}"
    )
    op.execute(f"REVOKE CREATE ON SCHEMA public FROM {ROLE_API}, {ROLE_EXECUTOR}")


def downgrade():
    if not _pg():
        return
    for role in (ROLE_EXECUTOR, ROLE_API, ROLE_MIGRATOR):
        op.execute(f"DROP ROLE IF EXISTS {role}")
