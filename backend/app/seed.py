from sqlalchemy import select

from app.auth import DEV_USER
from app.config import settings
from app.db import Session, apply_session_context
from app.models import Source, Subscription, Tenant
from app.tenancy import grant_executor_schema, provision_tenant

DEMO_TENANT = "00000000-0000-0000-0000-000000000010"


def main():
    if settings().environment != "development":
        raise RuntimeError("Seed demo somente em development")
    with Session.begin() as db:
        if db.get(Tenant, DEMO_TENANT) is None:
            provision_tenant(
                db,
                "Loja de Tintas Demo",
                DEV_USER,
                tenant_id=DEMO_TENANT,
            )
            db.add(Subscription(tenant_id=DEMO_TENANT))
        elif db.get_bind().dialect.name == "postgresql":
            tenant = db.get(Tenant, DEMO_TENANT)
            if tenant is not None:
                grant_executor_schema(db.connection(), tenant.schema_name)
        if not db.scalar(select(Source).where(Source.tenant_id == DEMO_TENANT)):
            apply_session_context(db, tenant_id=DEMO_TENANT, user_id=DEV_USER)
            db.add(Source(tenant_id=DEMO_TENANT, name="Vendas demonstrativas", kind="csv"))
    print("Seed pronto. Organização:", DEMO_TENANT)


if __name__ == "__main__":
    main()
