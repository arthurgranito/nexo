---
name: nexo-dev-quality
description: >-
  Avalia qualidade de uma rodada Nexo: ruff, pytest, typecheck/build e evals sintéticos
  quando existirem. Produz tabela de checks e falhas. Use após implementação ou antes de
  gate QA-001/BE-011; nunca com dados de produção.
---

# nexo-dev-quality

Papel de **Avaliador de qualidade** (desenvolvimento). Distinto do nó Verificador analítico (soma/unidade no chat).

## Escopo

- Regressão automatizada da rodada ou PR.
- Quando BE-007+: subset ou gate via [nexo-eval](../nexo-eval/SKILL.md) com fixtures.
- Release readiness **informativo** apenas — decisão de deploy é humana + [nexo-release](../nexo-release/SKILL.md).

## Arquivos permitidos

| Ação | Paths |
|------|--------|
| Leitura | Repositório inteiro |
| Escrita | `evals/**`, entradas em `docs/validacao.md`, anexos citados no relatório |
| Escrita (não) | Código de feature sem acordo — reportar falha ao implementador |

## Documentos obrigatórios

[AGENTS.md](../../../AGENTS.md), [roadmap.md](../../../docs/roadmap.md) (metas QA-001/BE-011), [validacao.md](../../../docs/validacao.md).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| Escopo | sim | Ticket, SHA ou branch |
| Camadas tocadas | sim | backend / frontend / ambos |
| Modo eval | se analítico | `dev` ou `gate` |

## Passos

1. Backend: `ruff check` nos paths tocados; `pytest` relevante (incl. `test_*_pg.py` se auth/tenant).
2. Frontend: `npm run typecheck`, `npm run build` se UI alterada.
3. Skills: `pytest backend/tests/test_cursor_skills.py` se `.cursor/skills` mudou.
4. Eval (quando harness existir): rodar com mock/fixture; reportar acurácia, cobertura, erro confiante, custo, p95 conforme ticket.
5. Consolidar tabela check × status.

## Critérios de saída

Relatório markdown:

| Check | Comando | Status | Notas |
|-------|---------|--------|-------|

- Falhas: trecho de log **sem** secrets.
- Eval: versão do conjunto, N casos, métricas vs meta do roadmap.
- **Veredicto:** pronto para integração / bloqueado / bloqueado só em PG.

## Limites

- **Proibido**: deploy, enviar dados reais a LLM, inventar métricas não medidas.
- **Proibido**: compras, mensagens externas, reduzir gate QA-001 para passar.
- Revisão aprovada não substitui execução pelo agente principal.

## Exemplo

**Pedido:** "Qualidade pós BE-002."

**Ação:** `ruff check backend/app/auth.py` + `pytest backend/tests/test_auth.py` → tabela → veredicto.

## Referências

- [agentes-desenvolvimento.md](../../../docs/agentes-desenvolvimento.md)
