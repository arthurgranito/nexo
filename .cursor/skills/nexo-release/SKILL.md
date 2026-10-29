---
name: nexo-release
description: >-
  Checklist de release Nexo: migrations Alembic, backup/restore, rollback de imagem,
  cotas/rate limit, separação de ambientes e configuração segura. Use antes de staging,
  piloto pago, INF-002/INF-003, QA-002 ou quando o usuário pedir go-live, restore ou
  verificação operacional — sem executar deploy não autorizado.
---

# nexo-release

Preparação e verificação operacional local/staging. Deploy em produção só com ordem explícita do usuário.

## Documentos obrigatórios

[docs/operacao.md](../../../docs/operacao.md), [decisoes.md](../../../docs/decisoes.md) (ADR-006, ADR-007),
[roadmap.md](../../../docs/roadmap.md) (INF-002, INF-003, BE-013, QA-002), [AGENTS.md](../../../AGENTS.md).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| Ambiente alvo | sim | `development` \| `staging` \| `production` (production = checklist only unless authorized) |
| Revision Alembic head | sim | `backend/migrations/versions/*` |
| Artefatos deploy | se existirem | `docker-compose.production.yml`, `deploy/backup.sh`, `deploy/Caddyfile` |
| Evidência prévia | não | `docs/progress.md`, `docs/validacao.md` |

## Passos

### 1. Configuração e ambientes (INF-002)

- `ENVIRONMENT` correto; `DEV_AUTH` rejeitado fora de development (`backend/app/config.py`).  
- Secrets via env/secret manager — nunca na imagem ou Git.  
- Healthchecks API/worker; logs sem tokens (ver `docs/operacao.md`).

### 2. Migrations

- Revisar cadeia Alembic; expand/contract para mudanças destrutivas.  
- Ensaiar upgrade em DB descartável (Compose local):  
  `alembic upgrade head` com role migrator, não usuário executor analítico.  
- Confirmar rollback documentado ou fix-forward; **não** reescrever revisions já aplicadas.

### 3. Roles e RLS (pré-requisito de release)

- Migrator ≠ API ≠ `nexo_executor`; RLS ativo no plano de controle (BE-001/003).  
- Skill **nexo-tenant-review** se release incluir mudanças de auth/dados.

### 4. Backup e restore (INF-003)

- Script/alvo: `deploy/backup.sh`, procedimento `deploy/restore.md`.  
- Backup cifrado **fora** do disco da VPS; restore em instância descartável.  
- Validar contagens + consulta de fumaça pós-restore — não basta exit 0 do dump.

### 5. Rollback

- App: reverter imagem/tag anterior; migration reversa só se testada.  
- Dados: versão publicada anterior permanece se publish falhou (conector).

### 6. Cotas e limites (BE-013)

- Verificar `backend/app/limits.py` / middleware quando implementados: 429, Retry-After, Redis atômico.  
- Upload max, concorrência por tenant, budget de modelo reservado antes da chamada.

### 7. Checks automatizados

```bash
cd backend && ruff check . && pytest -q
cd frontend && npm run typecheck && npm run build
```

Registrar o que não pôde rodar (ex.: sem Docker/PostgreSQL).

## Critérios de saída

Checklist markdown:

| Item | Status | Evidência |
|------|--------|-----------|
| Migrations testadas | pass/fail/skip | comando + revision |
| DEV_AUTH isolado | pass/fail | config |
| Backup/restore ensaiado | pass/fail/skip | log/data restore |
| Cotas | pass/fail/n/a | teste ou código |
| CI verde | pass/fail | link ou saída |

Incluir **RPO/RTO** declarados vs medidos (piloto: metas em `docs/operacao.md`).  
Atualizar `docs/progress.md` ou `docs/validacao.md` quando concluir verificação de ticket INF.

## Limites

- **Proibido**: deploy em VPS/produção, `docker push`, alterar DNS/TLS, enviar e-mail/Resend real, ativar cobrança Asaas, WhatsApp live.  
- **Proibido**: compras, contratar VPS, mensagens externas ou a clientes.  
- **Não** declarar backup pronto só porque `pg_dump` terminou.  
- **Não** usar Compose local como manifesto de produção sem INF-002.  
- Comandos locais destrutivos apenas em volumes de teste; migrations em produção exigem autorização explícita.

## Exemplo curto

**Pré-piloto staging:**

1. `ENVIRONMENT=staging`, `DEV_AUTH=false`.  
2. `docker compose up -d postgres redis` → `alembic upgrade head`.  
3. `pytest backend/tests/test_tenancy_pg.py backend/tests/test_rls_pg.py -q`.  
4. Simular restore: subir segundo Postgres, restaurar dump de teste, rodar uma query no tenant fixture.  
5. Reportar skip em backup cifrado externo se script ainda não existir (INF-003 pendente).

## Referências

- Deploy e incidentes: `docs/operacao.md`  
- Dependências/congelamento: INF-001, `backend/requirements.lock`  
- Telemetria alvo: `backend/app/telemetry.py` (INF-003)
