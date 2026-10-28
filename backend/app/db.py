from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session as OrmSession, sessionmaker

from app.config import api_database_url, settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings().database_url, pool_pre_ping=True)
api_engine = create_engine(api_database_url(), pool_pre_ping=True)
Session = sessionmaker(engine, expire_on_commit=False)
ApiSession = sessionmaker(api_engine, expire_on_commit=False)


def apply_session_context(
    db: OrmSession, *, tenant_id: str | None = None, user_id: str | None = None
) -> None:
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return
    if tenant_id is not None:
        db.execute(
            text("SELECT set_config('app.current_tenant_id', :value, true)"),
            {"value": tenant_id},
        )
    if user_id is not None:
        db.execute(
            text("SELECT set_config('app.current_user_id', :value, true)"),
            {"value": user_id},
        )


def get_db():
    with ApiSession() as session:
        yield session
