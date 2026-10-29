---
name: nexo-dev-implementer
description: >-
  Implementa um único ticket do roadmap Nexo de ponta a ponta (código + testes mínimos),
  respeitando AGENTS.md e dependências já registradas em progress.md. Use quando o
  usuário pedir implementar BE-xxx, FE-xxx, INF-xxx ou retomar uma fase do MVP.
---

# nexo-dev-implementer

Papel de **Implementador do ticket**. Não confundir com nós LangGraph do produto.

## Escopo

- Um ticket por rodada, conforme [roadmap.md](../../../docs/roadmap.md) e sequência em [prompts.md](../../../docs/prompts.md).
- Inspecionar implementação atual **antes** de editar.
- Dependências: só tickets marcados concluídos em [progress.md](../../../docs/progress.md) ou explicitamente autorizados pelo usuário.
- Proibido: simular integrações como reais, inventar credenciais/métricas, usar dados de produção.

## Arquivos permitidos

| Permitido | Restrição |
|-----------|-----------|
| Paths citados no ticket (roadmap) | Não expandir escopo a tickets futuros |
| `backend/tests/**`, `frontend/**/*.test.*` | Cobrir aceite e falhas principais |
| `backend/migrations/**` | Só quando o ticket exigir |
| `docs/progress.md` | Entrada da rodada concluída |
| `.cursor/skills/**` | Só se o ticket for skills/docs de agente |

**Proibido escrever:** `.env`, chaves, dumps de cliente, `requirements.lock` sem ticket INF-001.

## Documentos obrigatórios

[AGENTS.md](../../../AGENTS.md), [decisoes.md](../../../docs/decisoes.md), [arquitetura.md](../../../docs/arquitetura.md), ticket em [roadmap.md](../../../docs/roadmap.md).

## Entradas

| Entrada | Obrigatório | Uso |
|---------|-------------|-----|
| ID do ticket | sim | Ex.: `BE-004`, `INF-002` |
| Critérios de aceite | sim | Copiados do roadmap |
| Estado do progress | sim | Evitar reimplementar Setup concluído |

## Passos

1. Ler ticket + arquivos listados; mapear diff mínimo.
2. Implementar caminho vertical (API → persistência → teste, ou FE → contrato API).
3. Garantir `tenant_id` / membership em todo recurso novo (ADR-002/003).
4. Adicionar testes: aceite + acesso cruzado ou falha principal quando backend.
5. Rodar checks do ticket (ruff, pytest, typecheck/build se frontend).
6. Atualizar [progress.md](../../../docs/progress.md) com commit, checks, limitações.

## Critérios de saída

Relatório markdown:

- **Ticket** e critérios de aceite endereçados (sim/não por item).
- **Arquivos alterados** (lista).
- **Evidência:** comandos e resultado resumido.
- **Limitações** honestas (stubs, contas pendentes).
- **Próximo ticket** sugerido pela sequência em prompts.md.

## Limites

- **Proibido**: deploy, compras, mensagens externas, criar contas em serviços sem autorização.
- **Proibido**: afirmar conector/IA/cobrança prontos quando só há stub.
- **Não** pedir aprovação para edições locais reversíveis já cobertas pelo ticket.
- Revisores paralelos não dispensam o integrador de rodar testes finais.

## Exemplo

**Pedido:** "Implemente BE-003."

**Ação:** migration RLS → repositórios com filtro → `test_rls_pg.py` com dois tenants → ruff + pytest → progress.md.

## Referências

- Orquestração de papéis: [agentes-desenvolvimento.md](../../../docs/agentes-desenvolvimento.md)
