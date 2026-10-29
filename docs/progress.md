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

## Contas pendentes

- Projeto Supabase real (URL + anon key) para login de produção/staging
- `DEV_AUTH` permanece apenas em development
