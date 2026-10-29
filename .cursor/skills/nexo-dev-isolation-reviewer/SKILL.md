---
name: nexo-dev-isolation-reviewer
description: >-
  Revisa isolamento multi-tenant em PRs e tickets Nexo (auth, RLS, repositórios, schemas,
  cache FE). Somente leitura na lógica de negócio; pode propor testes PG. Use após diff
  de backend/auth ou antes de QA-001/QA-002. Complementa nexo-tenant-review.
---

# nexo-dev-isolation-reviewer

Papel de **Revisor de isolamento** (desenvolvimento). Distinto do executor read-only analítico no produto.

## Escopo

- Diff ou módulo indicado (ticket, rota nova, conector, chat, memória).
- Validar ADR-002 (plano de controle + schema analítico) e ADR-003 (JWT + membership).
- Header/query de tenant **nunca** concede acesso.
- 404 indistinguível para recurso ausente vs outro tenant quando aplicável.

## Arquivos permitidos

| Ação | Paths |
|------|--------|
| Leitura | `backend/app/auth.py`, `tenancy.py`, `repositories.py`, `routes/**`, `frontend/lib/session.ts`, migrations RLS/roles |
| Escrita (preferencial) | `backend/tests/test_auth.py`, `test_rls_pg.py`, `test_tenancy_pg.py`, fixtures de tenant |
| Escrita (evitar) | Lógica em `backend/app/**` — reportar achado ao implementador |

## Documentos obrigatórios

[decisoes.md](../../../docs/decisoes.md) ADR-002/003, [arquitetura.md](../../../docs/arquitetura.md), [AGENTS.md](../../../AGENTS.md).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| Escopo | sim | PR, ticket ou lista de arquivos |
| `tenant_a`, `tenant_b` | para PG | UUIDs fixture; nunca cliente real |
| Endpoints/tabelas novos | sim | Matriz recurso × tenant |

## Passos

1. Executar checklist em [nexo-tenant-review](../nexo-tenant-review/SKILL.md) nos eixos tocados pelo diff.
2. Grep `tenant_id`, `Access`, `require_membership`, `get_access` nas rotas novas.
3. Confirmar repositório não aceita tenant do body sem validar membership.
4. Se gap: esboçar teste PG ou citar teste existente.
5. Emitir relatório; **não** declarar deploy seguro.

## Critérios de saída

Relatório markdown:

- **Resumo:** pass/fail por eixo (auth, membership, RLS, repo, cache, retrieval).
- **Achados:** severidade bloqueante/alto/médio, arquivo e linha ou teste faltante.
- **Evidências:** comandos `pytest` executados ou reprodução manual documentada.
- **Veredicto:** bloqueante para merge ou ressalvas.

Gate mínimo: JWT inválido → 401; tenant B não lê/escreve dados de A no PostgreSQL real.

## Limites

- **Proibido**: deploy, alterar Supabase/produção, service role no frontend, tokens reais em logs.
- **Proibido**: compras, mensagens externas, aprovar go-live — revisão ≠ release.
- **Não** afirmar isolamento só por schema separado sem RLS + roles + teste.

## Exemplo

**Pedido:** "Revisar listagem de conversas no PR."

**Ação:** rota usa `Access`? repositório filtra `tenant_id`? teste A não vê `conversation_id` de B → relatório pass/fail.

## Referências

- [agentes-desenvolvimento.md](../../../docs/agentes-desenvolvimento.md)
