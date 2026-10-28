# Validação da entrega — 28/10/2026

## Executado com sucesso

- Backend: **18 testes passaram** (9,15 s na execução final).
- Ruff: `All checks passed`.
- Python: compilação de `app` e `migrations` sem erros.
- Alembic em SQLite: `upgrade head`, `check` (nenhuma operação nova), seed, `downgrade base`
  e novo `upgrade head`, todos concluídos.
- Frontend: `npm ci`, `npm run typecheck` e `npm run build`, Next.js 15.5.28, saída estática
  da página e standalone concluída. Lockfile npm incluído.
- Compose: `docker compose config --quiet` com cópia temporária do `.env.example`, sem erros.

Os testes verificam ausência de token, membership de outra organização, criação/duplicação
de fonte, DTO que rejeita credenciais arbitrárias sem ecoá-las, resposta de chat sem inventar
dados, recurso inacessível na correção, spec de dashboard restrita e SELECT com allowlist,
LIMIT e bloqueios de escrita/função perigosa/consulta fora do catálogo.

## Limites da evidência

Docker Desktop estava com o motor Linux desligado. Não foram construídas/executadas imagens,
nem validados PostgreSQL, roles, RLS, pgvector ou Redis/ARQ de ponta a ponta. Os testes da API
usam SQLite isolado; eles verificam o comportamento da aplicação, não o isolamento real do banco.
Os gates PostgreSQL e produção estão nos tickets BE-001/003/008 e QA-001.

TestClient no Windows ficou bloqueado ao criar socket interno do asyncio dentro da sandbox;
a suíte passou ao executar fora dela. O primeiro build compilou, mas emitiu EPERM na cópia
standalone; a repetição fora da sandbox concluiu sem esse aviso.

Não houve conexão a conta real Supabase/Google/Meta/Asaas/Resend, chamada paga de modelo,
publicação, mensagem a terceiros ou tratamento de dados empresariais reais.

As versões Python usam intervalos em pyproject.toml; resolução congelada com hashes permanece
no INF-001. A migration inicial foi congelada em DDL explícito. Arquivos de cache, node_modules,
ambientes locais e credenciais não fazem parte do ZIP.
