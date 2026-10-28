"""RLS fail-closed no plano de controle para a role nexo_api."""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

ROLE_API = "nexo_api"

TENANT_TABLES = (
    "audit_events",
    "conversations",
    "dashboards",
    "integrations",
    "semantic_rules",
    "sources",
    "subscriptions",
    "usage_events",
    "webhook_events",
    "datasets",
    "messages",
    "report_schedules",
    "sync_runs",
    "corrections",
    "query_runs",
)


def _pg() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _tenant_policy(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.execute(
        f"""
        CREATE POLICY tenant_isolation ON {table}
          USING (tenant_id = current_setting('app.current_tenant_id', true))
          WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true))
        """
    )


def upgrade():
    if not _pg():
        return
    for table in TENANT_TABLES:
        _tenant_policy(table)
    op.execute("ALTER TABLE memberships ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE memberships FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS membership_read ON memberships")
    op.execute(
        """
        CREATE POLICY membership_read ON memberships
          FOR SELECT
          USING (user_id = current_setting('app.current_user_id', true))
        """
    )
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenants FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tenant_membership_read ON tenants")
    op.execute(
        """
        CREATE POLICY tenant_membership_read ON tenants
          FOR SELECT
          USING (
            id IN (
              SELECT tenant_id FROM memberships
              WHERE user_id = current_setting('app.current_user_id', true)
            )
          )
        """
    )
    op.execute("DROP POLICY IF EXISTS tenant_owner_read ON tenants")
    op.execute(
        """
        CREATE POLICY tenant_owner_read ON tenants
          FOR SELECT
          USING (current_user IN ('nexo', 'nexo_migrator'))
        """
    )
    op.execute("DROP POLICY IF EXISTS tenant_provision_insert ON tenants")
    op.execute(
        """
        CREATE POLICY tenant_provision_insert ON tenants
          FOR INSERT
          WITH CHECK (current_user IN ('nexo', 'nexo_migrator'))
        """
    )
    op.execute("DROP POLICY IF EXISTS membership_owner_read ON memberships")
    op.execute(
        """
        CREATE POLICY membership_owner_read ON memberships
          FOR SELECT
          USING (current_user IN ('nexo', 'nexo_migrator'))
        """
    )
    op.execute("DROP POLICY IF EXISTS membership_provision ON memberships")
    op.execute(
        """
        CREATE POLICY membership_provision ON memberships
          FOR INSERT
          WITH CHECK (current_user IN ('nexo', 'nexo_migrator'))
        """
    )
    op.execute("DROP POLICY IF EXISTS membership_admin_delete ON memberships")
    op.execute(
        """
        CREATE POLICY membership_admin_delete ON memberships
          FOR DELETE
          USING (current_user IN ('nexo', 'nexo_migrator'))
        """
    )


def downgrade():
    if not _pg():
        return
    for table in TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS membership_read ON memberships")
    op.execute("ALTER TABLE memberships DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tenant_owner_read ON tenants")
    op.execute("DROP POLICY IF EXISTS tenant_provision_insert ON tenants")
    op.execute("DROP POLICY IF EXISTS tenant_membership_read ON tenants")
    op.execute("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS membership_owner_read ON memberships")
    op.execute("DROP POLICY IF EXISTS membership_provision ON memberships")
    op.execute("DROP POLICY IF EXISTS membership_admin_delete ON memberships")
