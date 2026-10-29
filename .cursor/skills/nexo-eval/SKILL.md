---
name: nexo-eval
description: >-
  Monta gabaritos sintéticos, executa harness de avaliação do chat analítico Nexo e
  gera relatório reproduzível (acurácia, cobertura, erro confiante, custo, latência).
  Use para BE-007/BE-011, gate do piloto, comparar modelos ou validar regressão após
  correções aprovadas — sempre com fixtures, nunca dados de produção.
---

# nexo-eval

Avaliação offline/reprodutível. Não envia dados reais de clientes a provedores de modelo.

## Documentos obrigatórios

[arquitetura.md](../../../docs/arquitetura.md) (gate do piloto, estados finais),
[decisoes.md](../../../docs/decisoes.md), [AGENTS.md](../../../AGENTS.md),
ticket BE-011 em [roadmap.md](../../../docs/roadmap.md) (metas do conjunto finito).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| Versão alvo | sim | Git SHA ou tag + `schema_version` / dataset fixture |
| Conjunto de casos | sim | `evals/cases.jsonl` (criar se ausente) |
| Modo | sim | `dev` (subset rápido) ou `gate` (≥60 casos, holdout separado) |
| Adapter LLM | se BE-007+ | `backend/app/llm.py` — fixture/mock ou provedor configurado localmente |

## Formato de caso (JSONL)

Uma linha JSON por caso, campos mínimos:

```json
{
  "id": "sale_total_jan",
  "tenant_fixture": "tenant_alpha",
  "question": "Qual foi o faturamento líquido em janeiro?",
  "expect": {
    "final_state": "answered",
    "metric": "revenue_net",
    "period": "2026-01",
    "tolerance_pct": 0.01
  },
  "tags": ["numeric", "period", "returns"]
}
```

Incluir casos de: ambiguidade (`needs_clarification`), fonte stale, vazio, injection em célula, vazamento (pergunta que exigiria tenant B).

## Passos

1. **Fixtures de dados** — Dataset sintético publicado no schema do tenant fixture (seed ou test helper); nunca dump de produção.  
2. **Gabarito** — Valores esperados calculados deterministicamente (SQL ou script), não "olhômetro" do modelo.  
3. **Separar holdout** — Casos `split: holdout` não usados para tuning de prompt; registrar contagem.  
4. **Executar harness** — Alvo: `backend/app/evals.py`, `evals/report.py` (criar conforme BE-011); cada caso registra `request_id`, estado final, custo/tokens se houver LLM.  
5. **Métricas** — Acurácia entre respondidas, cobertura, erro confiante, abstenção, p95 latência, custo médio (`docs/arquitetura.md`).  
6. **Relatório** — Arquivo versionado ex.: `evals/reports/<git-sha>.md` + JSON bruto `evals/reports/<git-sha>.json` para diff.  
7. **Checks** — `pytest` nos componentes determinísticos; eval completo documentado se LLM indisponível.

## Critérios de saída

- Relatório reproduzível: comando exato, SHA, contagem de casos, métricas, lista de falhas com `case_id` e motivo.  
- Holdout documentado; sem alegar 100% fora do conjunto.  
- Falhas classificadas: setup, SQL, semântica, verificador, vazamento.  
- `docs/progress.md` atualizado quando eval for gate de ticket.

Meta de **planejamento** do piloto (conjunto finito): ver arquitetura — não prometer universalmente.

## Limites

- **Proibido**: dados reais de cliente, prompts com PII, deploy, publicar relatório externamente.  
- **Proibido**: compras, mensagens externas (incl. stakeholders), marcar produto "pronto" só porque eval dev passou.  
- **Não** treinar ou fine-tune com o gabarito; eval mede comportamento atual.  
- **Não** chamar modelo em CI sem secret configurado — usar mock/fixture e documentar gap.  
- Execução local reversível — não pedir aprovação para criar/editar `evals/*` e testes.

## Exemplo curto

```bash
# Quando harness existir (BE-011)
cd backend && pytest tests/test_evals.py -q
python -m evals.report --cases ../evals/cases.jsonl --split gate --out ../evals/reports/local-dev.json
```

**Subset dev (3 casos):** numeric + ambiguous + cross_tenant_leak → esperado `answered`, `needs_clarification`, `refused`/`failed` sem dados de B.

## Referências

- Estados finais: `docs/arquitetura.md`  
- Correção e regressão: BE-010, skill nexo-tenant-review para casos de vazamento  
- Código alvo: `backend/app/agents.py`, `backend/app/evals.py` (a implementar), `evals/cases.jsonl`
