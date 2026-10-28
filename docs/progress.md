# Progresso de implementação

Registro por ticket (commit, checks, limitações). O roadmap não substitui esta evidência.

## INF-001 — Congelar dependências

- **Commit:** (pendente registro local)
- **Checks:** `pip install --require-hashes -r backend/requirements.lock`; ruff; pytest; frontend typecheck/build
- **Limitações:** pacote editable instalado com `--no-deps` após o lock

## BE-001 — Tenant e papéis PostgreSQL

- **Arquivos:** `backend/app/tenancy.py`, `backend/migrations/versions/0002_roles.py`, `backend/tests/test_tenancy_pg.py`
- **Checks:** pytest PostgreSQL (CI service)

## BE-002 — Sessão Supabase e autorização

- **Arquivos:** `backend/app/auth.py`, `backend/tests/test_auth.py`

## BE-003 — RLS e repositórios

- **Arquivos:** `backend/migrations/versions/0003_rls.py`, `backend/app/repositories.py`, `backend/tests/test_rls_pg.py`

## FE-001 — Login e organização

- **Arquivos:** `frontend/app/login/page.tsx`, `frontend/lib/supabase.ts`, `frontend/app/app/layout.tsx`

## Contas pendentes

- Projeto Supabase real (URL + anon key) para login de produção/staging
- `DEV_AUTH` permanece apenas em development
