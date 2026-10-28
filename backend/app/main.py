import logging
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agents import graph
from app.auth import Access, access, editor, user_id
from app.config import settings
from app.db import apply_session_context, get_db
from app.models import AuditEvent, Conversation, Correction, Dashboard, Message, Source
from app.repositories import Repositories
from app.schemas import CorrectionCreate, DashboardCreate, Question, SourceCreate, SourceRead

app = FastAPI(title="Nexo API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings().cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "X-Tenant-ID", "Content-Type"],
)


@app.middleware("http")
async def request_id(request: Request, call_next):
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


def error(request, status, code, detail):
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "detail": detail,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return error(request, exc.status_code, "http_error", exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return error(
        request,
        422,
        "validation_error",
        [{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()],
    )


@app.exception_handler(Exception)
async def unhandled(request, exc):
    logging.getLogger("nexo").error(
        "Unhandled failure request_id=%s type=%s",
        getattr(request.state, "request_id", None),
        type(exc).__name__,
    )
    return error(request, 500, "internal_error", "Falha interna")


def commit(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Registro duplicado ou referência inválida") from None


def audit(db, ctx, action, resource):
    db.add(
        AuditEvent(
            tenant_id=ctx.tenant_id,
            actor_id=ctx.user_id,
            action=action,
            resource_id=resource,
        )
    )


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    apply_session_context(db, user_id="00000000-0000-0000-0000-000000000001")
    db.scalar(select(1))
    return {"status": "ready"}


@app.get("/v1/me/organizations")
def organizations(uid: str = Depends(user_id), db: Session = Depends(get_db)):
    repos = Repositories(db, tenant_id=None, user_id=uid)
    return {"items": [{"id": m.tenant_id, "role": m.role} for m in repos.memberships_for_user()]}


@app.get("/v1/sources", response_model=list[SourceRead])
def sources(
    ctx: Access = Depends(access),
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    repos = Repositories(db, tenant_id=ctx.tenant_id, user_id=ctx.user_id)
    return repos.sources(offset=offset, limit=limit)


@app.post("/v1/sources", response_model=SourceRead, status_code=201)
def create_source(
    body: SourceCreate, ctx: Access = Depends(editor), db: Session = Depends(get_db)
):
    repos = Repositories(db, tenant_id=ctx.tenant_id, user_id=ctx.user_id)
    obj = Source(tenant_id=ctx.tenant_id, **body.model_dump())
    repos.add_source(obj)
    try:
        db.flush()
        audit(db, ctx, "source.created", obj.id)
        commit(db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Já existe uma fonte com esse nome") from None
    return obj


@app.post("/v1/chat", status_code=201)
def chat(body: Question, ctx: Access = Depends(access), db: Session = Depends(get_db)):
    repos = Repositories(db, tenant_id=ctx.tenant_id, user_id=ctx.user_id)
    count = repos.count_sources()
    result = graph.invoke(
        {"question": body.text, "tenant_id": ctx.tenant_id, "source_count": count}
    )
    conv = Conversation(tenant_id=ctx.tenant_id, title=body.text[:180], user_id=ctx.user_id)
    repos.add_conversation(conv)
    db.flush()
    repos.add_message(
        Message(tenant_id=ctx.tenant_id, conversation_id=conv.id, role="user", content=body.text)
    )
    answer = Message(
        tenant_id=ctx.tenant_id,
        conversation_id=conv.id,
        role="assistant",
        content=result["answer"],
        evidence={"status": result["status"], "trace": result["trace"]},
    )
    repos.add_message(answer)
    db.flush()
    commit(db)
    return {
        "conversation_id": conv.id,
        "message_id": answer.id,
        "answer": answer.content,
        "status": result["status"],
        "trace": result["trace"],
    }


@app.post("/v1/corrections", status_code=201)
def correct(body: CorrectionCreate, ctx: Access = Depends(editor), db: Session = Depends(get_db)):
    repos = Repositories(db, tenant_id=ctx.tenant_id, user_id=ctx.user_id)
    message = repos.assistant_message(body.message_id)
    if message is None:
        raise HTTPException(404, "Resposta não encontrada")
    obj = Correction(tenant_id=ctx.tenant_id, **body.model_dump())
    repos.add_correction(obj)
    db.flush()
    audit(db, ctx, "correction.proposed", obj.id)
    commit(db)
    return {"id": obj.id, "status": obj.status}


@app.get("/v1/dashboards")
def dashboards(
    ctx: Access = Depends(access),
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    repos = Repositories(db, tenant_id=ctx.tenant_id, user_id=ctx.user_id)
    rows = repos.dashboards(offset=offset, limit=limit)
    return {"items": [{"id": d.id, "name": d.name, "spec": d.spec} for d in rows]}


@app.post("/v1/dashboards", status_code=201)
def create_dashboard(
    body: DashboardCreate, ctx: Access = Depends(editor), db: Session = Depends(get_db)
):
    repos = Repositories(db, tenant_id=ctx.tenant_id, user_id=ctx.user_id)
    obj = Dashboard(tenant_id=ctx.tenant_id, **body.model_dump())
    repos.add_dashboard(obj)
    db.flush()
    audit(db, ctx, "dashboard.created", obj.id)
    commit(db)
    return {"id": obj.id, "name": obj.name, "spec": obj.spec}
