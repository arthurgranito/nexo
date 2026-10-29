# Progresso de implementação

Registro por ticket (commit, checks, limitações). O roadmap não substitui esta evidência.

## INF-001 — Congelar dependências

- **Commit:** `79f4d8d`
- **Checks:** `pip install --require-hashes -r backend/requirements.lock`; ruff; pytest (29); frontend typecheck/build
- **Limitações:** pacote editable instalado com `--no-deps` após o lock

## BE-001 — Tenant e papéis PostgreSQL

- **Commit:** `a7e3203`
- **Arquivos:** `backend/app/tenancy.py`, `backend/migrations/versions/0002_roles.py`, `backend/tests/test_tenancy_pg.py`
- **Checks:** 3 testes PG (provisionamento, rollback, executor × schema vizinho)

## BE-002 — Sessão Supabase e autorização

- **Commit:** `6aec100`
- **Arquivos:** `backend/app/auth.py`, `backend/tests/test_auth.py`
- **Checks:** JWT sintético ES256 (válido/expirado/issuer), viewer, revogação, rotação JWKS cache

## BE-003 — RLS e repositórios

- **Commit:** `22534a4`
- **Arquivos:** `backend/migrations/versions/0003_rls.py`, `backend/app/repositories.py`, `backend/tests/test_rls_pg.py`
- **Checks:** 2 testes PG (leitura cruzada vazia, INSERT com tenant errado falha)

## FE-001 — Login e organização

- **Commit:** `e5c983f`
- **Arquivos:** `frontend/app/login/page.tsx`, `frontend/lib/supabase.ts`, `frontend/app/app/layout.tsx`
- **Checks:** `npm run typecheck`, `npm run build` (rotas `/login`, `/app`)

## Skills locais de desenvolvimento (docs/prompts.md)

- **Arquivos:** `.cursor/skills/nexo-tenant-review/SKILL.md`, `nexo-connector`, `nexo-eval`, `nexo-release`; `backend/tests/test_cursor_skills.py`
- **Checks:** `pytest tests/test_cursor_skills.py` (12); `ruff check tests/test_cursor_skills.py`
- **Limitações:** skills orientam o agente; harness `evals/` e conectores além do boilerplate ainda dependem dos tickets BE-004+ / BE-011

## Papéis de agente de desenvolvimento (docs/prompts.md — opcional)

- **Arquivos:** `docs/agentes-desenvolvimento.md`; `.cursor/skills/nexo-dev-implementer`, `nexo-dev-isolation-reviewer`, `nexo-dev-quality`, `nexo-dev-ux`; `backend/tests/test_cursor_skills.py` (8 skills)
- **Checks:** `pytest backend/tests/test_cursor_skills.py`; `ruff check backend/tests/test_cursor_skills.py`
- **Limitações:** definições portáveis apenas — nenhum agente LangGraph ou subagente foi executado nesta entrega; revisão não autoriza deploy

## MCPs de desenvolvimento (docs/prompts.md)

- **Arquivos:** `docs/mcp-desenvolvimento.md`; `.cursor/mcp.json.example`; `backend/tests/test_cursor_skills.py` (contrato MCP)
- **Checks:** `pytest backend/tests/test_cursor_skills.py`; `ruff check backend/tests/test_cursor_skills.py`
- **Limitações:** nenhum servidor MCP instalado ou conta conectada; servidor custom Nexo adiado até BE-011+; browser staging depende de `STAGING_BASE_URL` e login humano

## Contas pendentes

- Projeto Supabase real (URL + anon key) para login de produção/staging
- `DEV_AUTH` permanece apenas em development
