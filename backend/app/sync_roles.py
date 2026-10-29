"""Sincroniza senhas das roles PostgreSQL com variáveis de ambiente (idempotente)."""
from __future__ import annotations

import os

from sqlalchemy import create_engine, text

from app.config import settings


def _q(value: str) -> str:
    return value.replace("'", "''")


def main() -> None:
    url = settings().database_url
    if not url.startswith("postgresql"):
        return
    migrator_pw = os.environ.get("NEXO_MIGRATOR_PASSWORD", "nexo_migrator_local_dev_only")
    api_pw = os.environ.get("NEXO_API_PASSWORD", "nexo_api_local_dev_only")
    executor_pw = os.environ.get("NEXO_EXECUTOR_PASSWORD", "nexo_executor_local_dev_only")
    engine = create_engine(url, pool_pre_ping=True)
    with engine.begin() as conn:
        for role, password in (
            ("nexo_migrator", migrator_pw),
            ("nexo_api", api_pw),
            ("nexo_executor", executor_pw),
        ):
            conn.execute(text(f"ALTER ROLE {role} PASSWORD '{_q(password)}'"))
    print("Senhas das roles PostgreSQL sincronizadas.")


if __name__ == "__main__":
    main()
