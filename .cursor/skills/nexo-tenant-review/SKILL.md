---
name: nexo-tenant-review
description: >-
  Audita isolamento multi-tenant no Nexo: JWT/Supabase, memberships, RLS,
  repositórios com escopo, cache do frontend e retrieval de memória/embeddings.
  Use quando o usuário pedir revisão de tenant, vazamento entre organizações,
  auditoria de auth/RLS, teste de acesso cruzado, ou antes de gates QA-001/QA-002.
---

# nexo-tenant-review

Revisão sistemática de isolamento. Não altera produção nem executa deploy.

## Documentos obrigatórios

Leia antes de auditar: [AGENTS.md](../../../AGENTS.md), [decisoes.md](../../../docs/decisoes.md) (ADR-002, ADR-003),
[arquitetura.md](../../../docs/arquitetura.md) (execução segura, memória), [modelagem.md](../../../docs/modelagem.md).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| Escopo | sim | Ticket, PR ou módulo (`auth`, `repositories`, `routes/*`, `frontend/lib/session`) |
| `tenant_a`, `tenant_b` | para testes PG | UUIDs de fixtures ou seed; nunca dados de cliente real |
| Lista de endpoints/tabelas tocados | sim | Matriz recurso × filtro de tenant |
| Evidência existente | não | `backend/tests/test_*_pg.py`, `test_auth.py`, `test_rls_pg.py` |

## Passos

1. **Autenticação (ADR-003)**  
   - Confirmar validação ES256/RS256 via JWKS, `iss`, `aud`, `exp`, `sub` em `backend/app/auth.py`.  
   - `DEV_AUTH` só quando `ENVIRONMENT=development` (`backend/app/config.py`).  
   - Header ou query de tenant **nunca** concede acesso; tenant vem de `Membership` após `user_id`.

2. **Membership e papéis**  
   - Mapear `owner` / `admin` / `analyst` / `viewer` vs rotas mutáveis (`EDIT_ROLES`, `ADMIN_ROLES`).  
   - Revogação ou troca de membership deve negar imediatamente (teste em `backend/tests/test_auth.py`).

3. **Plano de controle e schema analítico (ADR-002)**  
   - Tabelas compartilhadas: filtro `tenant_id` + RLS em PostgreSQL (`backend/migrations/versions/0003_rls.py`).  
   - Dados importados: schema `t_<uuid sem hífens>` via `backend/app/tenancy.py`; role `nexo_executor` sem schema vizinho.

4. **Repositórios e rotas**  
   - Toda query mutável/listagem passa por `backend/app/repositories.py` ou equivalente com tenant da sessão.  
   - 404 indistinguível para recurso inexistente vs outro tenant (regra transversal em `docs/roadmap.md`).

5. **Cache frontend**  
   - Troca de organização invalida cache (`frontend/lib/session.ts`: `writeTenantId(..., invalidateCache)`).  
   - Não confiar em route guard; API revalida sempre.

6. **Retrieval / memória (quando existir)**  
   - Embeddings e exemplos indexados **por tenant**; invalidar ao mudar catálogo ou regra (`docs/arquitetura.md`).  
   - Checkpoints LangGraph com namespace do tenant.

7. **Evidência**  
   - Rodar ou estender testes PG de acesso cruzado; documentar falhas com request_id reproduzível.

## Critérios de saída

Relatório markdown com:

- **Resumo**: pass / fail por eixo (auth, membership, RLS, repositório, cache, retrieval).  
- **Achados**: severidade (bloqueante / alto / médio), arquivo, linha ou teste faltante.  
- **Testes**: comandos executados e resultado (`pytest backend/tests/test_tenancy_pg.py` etc.).  
- **Regressões sugeridas**: apenas patches locais reversíveis; aplicar sem pedir aprovação para testes/fixtures.

Gate mínimo alinhado a BE-002/BE-003: JWT inválido → 401; tenant B não lê/escreve dados de A no PostgreSQL real.

## Limites

- **Proibido**: deploy, SSH em VPS, alterar Supabase/produção, usar service role no frontend, copiar tokens reais para logs ou skills.  
- **Proibido**: compras, mensagens externas ou a clientes, criar contas externas sem autorização explícita do usuário.  
- **Não** afirmar isolamento completo só com schema separado; exigir RLS + roles + teste de conexão.  
- **Não** usar SQLite como única evidência para RLS (aceitar como complemento unitário).

## Exemplo curto

**Pedido:** "Revisar PR que adiciona listagem de conversas."

**Ação:** grep `tenant_id` e `get_access` na rota nova → verificar filtro no repositório → adicionar teste: user de tenant A com token válido recebe lista vazia ou 404 para `conversation_id` de B → reportar.

```python
# Padrão esperado (ilustrativo): tenant sempre da Access, não do body
access: Access = Depends(require_membership)
rows = repo.list_conversations(db, tenant_id=access.tenant_id, ...)
```

## Referências de código

- `backend/app/auth.py` — JWT, `Access`, membership  
- `backend/app/repositories.py` — escopo de tenant  
- `backend/app/tenancy.py` — schema analítico e grants  
- `backend/tests/test_rls_pg.py`, `test_tenancy_pg.py`, `test_auth.py`
