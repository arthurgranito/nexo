import os
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("DEV_AUTH", "true")
os.environ.setdefault("DEV_TOKEN", "test-token-long-enough-for-development")
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app
from app.auth import DEV_USER
from app.models import Membership, Source, Tenant

A = "00000000-0000-0000-0000-000000000010"
B = "00000000-0000-0000-0000-000000000020"

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory.begin() as db:
        db.add_all([Tenant(id=A, name="A", schema_name="t_a"), Tenant(id=B, name="B", schema_name="t_b")])
        db.flush()
        db.add(Membership(tenant_id=A, user_id=DEV_USER, role="owner"))
        db.add(Source(tenant_id=B, name="Segredo B", kind="csv"))
    def override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()

def headers(tenant=A):
    return {"Authorization": "Bearer test-token-long-enough-for-development", "X-Tenant-ID": tenant}

def test_no_token(client):
    assert client.get("/v1/sources", headers={"X-Tenant-ID": A}).status_code == 401

def test_tenant_boundary(client):
    assert client.get("/v1/sources", headers=headers()).json() == []
    assert client.get("/v1/sources", headers=headers(B)).status_code == 403

def test_create_duplicate_and_private_fields(client):
    body = {"name": "Vendas", "kind": "csv"}
    response = client.post("/v1/sources", json=body, headers=headers())
    assert response.status_code == 201
    assert "secret_ref" not in response.json()
    assert client.post("/v1/sources", json=body, headers=headers()).status_code == 409

def test_reject_credentials_in_public_source_dto(client):
    response = client.post("/v1/sources", headers=headers(), json={
        "name": "DB", "kind": "postgres", "password": "never-echo-this"})
    assert response.status_code == 422
    assert "never-echo-this" not in response.text

def test_chat_does_not_invent_data(client):
    response = client.post("/v1/chat", headers=headers(), json={"text": "Quanto vendi?"})
    assert response.status_code == 201
    assert response.json()["status"] == "needs_setup"
    assert "sincronize" in response.json()["answer"]

def test_cross_tenant_correction(client):
    response = client.post("/v1/corrections", headers=headers(), json={
        "message_id": "00000000-0000-0000-0000-000000000999",
        "reason": "O cálculo está incorreto", "proposed_rule": "Excluir devoluções"})
    assert response.status_code == 404

def test_dashboard_rejects_arbitrary_spec(client):
    response = client.post("/v1/dashboards", headers=headers(), json={
        "name": "Vendas", "spec": {"javascript": "alert(1)"}})
    assert response.status_code == 422
