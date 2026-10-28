import secrets
from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import apply_session_context, get_db
from app.models import Membership

DEV_USER = "00000000-0000-0000-0000-000000000001"
bearer = HTTPBearer(auto_error=False)
EDIT_ROLES = frozenset({"owner", "admin", "analyst"})
ADMIN_ROLES = frozenset({"owner", "admin"})


@lru_cache
def jwks():
    return jwt.PyJWKClient(settings().supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json")


def reset_jwks_cache() -> None:
    jwks.cache_clear()


def decode_supabase_token(token: str) -> str:
    cfg = settings()
    if not cfg.supabase_url:
        raise HTTPException(401, "Autenticação Supabase não configurada")
    try:
        key = jwks().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key.key,
            algorithms=["ES256", "RS256"],
            audience=cfg.supabase_audience,
            issuer=cfg.supabase_url.rstrip("/") + "/auth/v1",
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
        return str(UUID(claims["sub"]))
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(401, "Token inválido") from None


def user_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise HTTPException(401, "Bearer token obrigatório")
    cfg = settings()
    if cfg.dev_auth and secrets.compare_digest(credentials.credentials, cfg.dev_token):
        return DEV_USER
    return decode_supabase_token(credentials.credentials)


@dataclass
class Access:
    tenant_id: str
    user_id: str
    role: str


def access(
    x_tenant_id: str = Header(),
    uid: str = Depends(user_id),
    db: Session = Depends(get_db),
):
    try:
        tenant = str(UUID(x_tenant_id))
    except ValueError:
        raise HTTPException(400, "X-Tenant-ID inválido") from None
    apply_session_context(db, user_id=uid)
    membership = db.scalar(
        select(Membership).where(Membership.tenant_id == tenant, Membership.user_id == uid)
    )
    if membership is None:
        raise HTTPException(403, "Sem acesso à organização")
    apply_session_context(db, tenant_id=tenant, user_id=uid)
    return Access(tenant, uid, membership.role)


def editor(ctx: Access = Depends(access)):
    if ctx.role not in EDIT_ROLES:
        raise HTTPException(403, "Permissão de edição necessária")
    return ctx


def admin(ctx: Access = Depends(access)):
    if ctx.role not in ADMIN_ROLES:
        raise HTTPException(403, "Permissão administrativa necessária")
    return ctx
