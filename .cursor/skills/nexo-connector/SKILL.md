---
name: nexo-connector
description: >-
  Implementa ou revisa conectores Nexo no pipeline discover → extract → normalize →
  validate → publish, com idempotência, staging por tenant e secrets por referência.
  Use para CSV/Excel, Sheets, SQL externo, novo conector, sync worker, schema drift
  ou tickets BE-004/005/014/015/016 e docs/sincronizacao.md.
---

# nexo-connector

Guia de implementação vertical de conector. Não simula OAuth/API como se estivessem ativos sem código e testes.

## Documentos obrigatórios

[docs/sincronizacao.md](../../../docs/sincronizacao.md), [arquitetura.md](../../../docs/arquitetura.md),
[decisoes.md](../../../docs/decisoes.md) (ADR-005), [modelagem.md](../../../docs/modelagem.md), [AGENTS.md](../../../AGENTS.md).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| Tipo de fonte | sim | `csv`, `excel`, `google_sheets`, `postgres`, `mysql`, … |
| Ticket / escopo | sim | Ex.: BE-004 — arquivos alvo listados no roadmap |
| Fixtures sintéticas | sim | CSV/planilha pequena com casos de borda (locale, cabeçalho duplicado) |
| IDs existentes | após seed | `tenant_id`, `source_id` do plano de controle |

## Passos

1. **Discover** — Metadados sem secrets: abas, colunas candidatas, limites de tamanho, estado `needs_setup` se incompleto.  
2. **Extract(checkpoint)** — Job payload só IDs; credenciais resolvidas no backend; watermark/checkpoint persistido.  
3. **Normalize** — Determinístico (espaços, datas com locale, decimal, fórmulas sem cache); preservar originais no staging restrito.  
4. **Validate** — Colunas obrigatórias, linhas rejeitadas, totais de controle; schema drift bloqueia publicação automática quando aplicável.  
5. **Publish** — Snapshot + catálogo na **mesma transação** dentro do schema `t_*` autorizado; hash igual → no-op; falha mantém versão publicada anterior.

Estados: `pending → running → staged → validated → published`; erro → `failed`.

6. **Worker / fila** — Uma sync ativa por fonte; idempotência `tenant + source + versão`; advisory lock/lease; retries só transitórios (`docs/sincronizacao.md`).  
7. **Testes** — Caminho feliz, arquivo inválido/macro, reenvio idêntico, falha antes do commit, worker morto, revogação OAuth (quando existir), delete/reconciliação conforme tipo.

## Layout de código (alvo)

| Fase | Local típico (criar se ticket exigir) |
|------|----------------------------------------|
| Arquivos | `backend/app/connectors/files.py` |
| Sheets | `backend/app/connectors/google.py` |
| SQL externo | `backend/app/connectors/sql.py`, `network_policy.py` |
| Orquestração | `backend/app/ingestion.py`, `worker.py`, `catalog.py` |

Inspecionar implementação atual antes de editar; não duplicar módulos.

## Critérios de saída

- Conector expõe as cinco fases com contrato claro (funções ou classe documentada).  
- Nenhum secret, refresh token ou conteúdo de planilha em Redis/logs/job JSON.  
- Testes automatizados cobrem aceite do ticket e falhas principais (não espelhar implementação linha a linha).  
- README interno ou comentário mínimo só onde o contrato não for óbvio.  
- Atualizar `docs/progress.md` com commit, checks e limitações (ex.: "OAuth stub, polling não conectado").

## Limites

- **Proibido**: deploy, polling real em planilha de cliente, armazenar credenciais reais no Git, afirmar "Sheets conectado" com stub.  
- **Proibido**: compras, mensagens externas, criar projeto Google Cloud/Asaas sem autorização.  
- **Não** inferir delete silencioso em planilha sem política explícita.  
- **Não** usar LLM para normalização trivial (ver prompts MVP ingestão).  
- Mudanças locais reversíveis (fixtures, testes, código em branch) — executar sem pedir aprovação.

## Exemplo curto

**CSV piloto:** fixture `evals/fixtures/sales_ptbr.csv` com cabeçalho duplicado e data `01/02/2023`.

```text
discover → 3 colunas, 2 linhas válidas, 1 rejeitada (data ambígua sem locale)
normalize → locale pt-BR, coluna duplicada renomeada _2
validate → falha se coluna "valor" ausente
publish → hash H1; reupload H1 → no-op; H2 → nova versão, catálogo atualizado junto
```

## Referências

- Pipeline e idempotência: `docs/sincronizacao.md`  
- Publicação e catálogo: tickets BE-005, BE-015  
- Guardas atuais: `backend/app/worker.py`, `backend/app/sql_guard.py` (não substitui validação de ingestão)
