import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("DEV_AUTH", "true")
os.environ.setdefault("DEV_TOKEN", "test-token-long-enough-for-development")

from app.auth import DEV_USER, reset_jwks_cache  # noqa: E402
from app.config import Settings
from app.db import Base, get_db
from app.main import app
from app.models import Membership, Tenant

A = "00000000-0000-0000-0000-000000000010"
SUPABASE = "https://example-project.supabase.co"
PRIVATE = ec.generate_private_key(ec.SECP256R1())
PUBLIC = PRIVATE.public_key()


class _SigningKey:
    key = PUBLIC


def _token(**overrides):
    now = datetime.now(timezone.utc)
    claims = {
        "sub": DEV_USER,
        "iss": SUPABASE + "/auth/v1",
        "aud": "authenticated",
        "exp": now + timedelta(hours=1),
        "iat": now,
    }
    claims.update(overrides)
    return jwt.encode(claims, PRIVATE, algorithm="ES256", headers={"kid": "test-key"})


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory.begin() as db:
        db.add(Tenant(id=A, name="A", schema_name="t_a"))
        db.flush()
        db.add(Membership(tenant_id=A, user_id=DEV_USER, role="owner"))
        db.add(Membership(tenant_id=A, user_id="00000000-0000-0000-0000-000000000099", role="viewer"))
    def override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override
    cfg = Settings(
        environment="development",
        database_url="sqlite://",
        supabase_url=SUPABASE,
        supabase_audience="authenticated",
        dev_auth=False,
        dev_token="",
    )
    with patch("app.auth.settings", lambda: cfg), patch(
        "app.auth.jwks"
    ) as mock_jwks:
        mock_jwks.return_value.get_signing_key_from_jwt.return_value = _SigningKey()
        reset_jwks_cache()
        with TestClient(app) as c:
            yield c, factory
    app.dependency_overrides.clear()
    reset_jwks_cache()


def headers(token: str, tenant: str = A):
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": tenant}


def test_valid_jwt(client):
    http, _factory = client
    assert http.get("/v1/sources", headers=headers(_token())).status_code == 200


def test_expired_jwt(client):
    http, _factory = client
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    token = _token(exp=int(past.timestamp()))
    assert http.get("/v1/sources", headers=headers(token)).status_code == 401


def test_wrong_issuer(client):
    http, _factory = client
    token = _token(iss="https://evil.example/auth/v1")
    assert http.get("/v1/sources", headers=headers(token)).status_code == 401


def test_viewer_cannot_create_source(client):
    http, _factory = client
    viewer_token = _token(sub="00000000-0000-0000-0000-000000000099")
    response = http.post(
        "/v1/sources",
        headers=headers(viewer_token),
        json={"name": "Bloqueado", "kind": "csv"},
    )
    assert response.status_code == 403


def test_membership_revocation(client):
    http, factory = client
    token = _token()
    assert http.get("/v1/sources", headers=headers(token)).status_code == 200
    with factory.begin() as db:
        db.execute(
            delete(Membership).where(
                Membership.tenant_id == A, Membership.user_id == DEV_USER
            )
        )
    assert http.get("/v1/sources", headers=headers(token)).status_code == 403


def test_jwks_cache_rotation(client):
    http, _factory = client
    first = http.get("/v1/sources", headers=headers(_token()))
    assert first.status_code == 200
    reset_jwks_cache()
    second = http.get("/v1/sources", headers=headers(_token()))
    assert second.status_code == 200
