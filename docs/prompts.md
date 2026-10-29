# Prompts para Claude, Cursor e Codex

Os prompts são agnósticos ao editor. Abra a raiz Nexo e use um ticket por rodada. Não envie
todo o roadmap como ordem para implementar tudo num turno. Use branches e revisão humana.
Ferramentas de desenvolvimento são distintas dos agentes que atendem clientes no produto.

## Prompt base (prefixe em todas as fases)

```text
Você está no projeto Nexo. Leia AGENTS.md, README.md, docs/decisoes.md, docs/arquitetura.md
e o ticket solicitado em docs/roadmap.md. Antes de editar, inspecione a implementação atual.
Implemente apenas o ticket indicado e suas dependências já autorizadas. Não simule integrações
como se fossem reais, não use dados de produção e não invente credenciais ou métricas.
Mantenha isolamento por tenant no banco e no código. Produza testes que demonstrem o aceite
e os principais cenários de falha. Execute os checks relevantes e reporte arquivos alterados,
evidência, limitações e próximo ticket. Não faça deploy, compras ou comunicação externa.
```

## Setup -> FEITO

```text
Implemente INF-001, depois BE-001/002/003 e FE-001, um commit por ticket. Primeiro apresente
o plano curto de alterações e execute as que não exigem contas reais. Configure migrations
PostgreSQL, roles migrator/API/executor, RLS e testes com dois tenants. Complete login
Supabase sem service role no frontend. Preserve dev auth só em development. Termine apenas
quando CI, migrations e testes de acesso cruzado passarem; registre qualquer conta pendente.
```

## MVP — ingestão

```text
Implemente BE-004/005/006 e FE-002 nessa ordem. Use docs/sincronizacao.md como contrato.
Construa upload CSV primeiro; depois Excel. Preview e aprovação precedem publicação.
Reenvio do mesmo arquivo é no-op; falha não altera versão publicada. Inclua devolução,
moeda pt-BR, datas ambíguas e cabeçalhos duplicados nas fixtures. A entrevista deve gerar
regras pendentes até confirmação do responsável. Não chamar LLM para normalização trivial.
```

## MVP — inteligência

```text
Implemente BE-007/008/009 como caminho vertical. Escolha provedor/modelo por avaliação,
e defina adapter para substituí-lo. Não presuma acesso ao Windy ou Seedash. Crie plano
estruturado, SQL validado por AST, role readonly, timeout e resposta com proveniência.
Limite tentativas e custo por pergunta. Teste ambiguidade, prompt injection em células,
SQL perigoso, fonte stale, dados vazios e acesso cruzado. Sem evidência, peça esclarecimento.
```

## MVP — produto e gate

```text
Implemente BE-010/011/012/013 e FE-003/004, respeitando dependências. Correção precisa
aprovação e regressão; gráfico usa resultado validado do mesmo tenant. Monte 60 casos
com gabarito, incluindo holdout, e reporte acurácia entre respondidas, cobertura, erro
confiante, custo e p95. Rode QA-001 e verifique restauração INF-003 antes do piloto.
Não reduzir o gate para caber no cronograma. Crie relatório do que ainda impede vender.
```

## v1 — fontes conectadas

```text
Implemente BE-014/015/016 e FE-005 conforme docs/sincronizacao.md. OAuth por tenant com
state/TTL, secrets cifrados, polling, dedupe, staging e publicação atômica. onEdit é só sinal,
não garantia de completude. Teste refresh revogado, 429, mudança de schema, delete e job
morto após commit. Para banco externo: TLS, role readonly, allowlist e proteção SSRF.
```

## v1 — comercial e operação

```text
Implemente BE-017/018/019, FE-006/007 e QA-002. Comece em sandbox Resend/Asaas. Preview
não envia; cobrança só muda estado após webhook verificado e reconciliado. Deduplicar
eventos e entregas. Defina retenção, exportação, exclusão e backup. Faça teste de carga,
restore e rollback. Não ativar pagamentos ou envios reais sem configuração e autorização.
```

## v2 — WhatsApp

```text
Implemente BE-020/021/022, FE-008 e QA-003. Separe totalmente as ferramentas do contato
externo das ferramentas do administrador interno. Verifique assinatura do corpo bruto,
tenant por integração cadastrada, opt-out, janela/template vigente e handoff. Teste mensagens
duplicadas, fora de ordem, pedido alheio, jailbreak e resposta atrasada após assumir humano.
Use sandbox e fixtures; mantenha rollout desativado até gate por organização.
```

## Criar skills locais de desenvolvimento -> FEITO

```text
Crie skills versionadas neste repositório, sem instalar globalmente:
1. nexo-tenant-review: auditar autenticação, memberships, filtros/RLS, cache e retrieval;
2. nexo-connector: construir conector seguindo discover/extract/normalize/validate/publish;
3. nexo-eval: criar gabaritos sintéticos, executar avaliação e produzir relatório reproduzível;
4. nexo-release: verificar migration, backup, restore, rollback, cotas e configuração.
Para cada skill, escreva SKILL.md com gatilhos precisos, entradas, passos, critérios de saída
e limites. Não pedir aprovação para mudanças locais reversíveis já autorizadas. Nunca dar
à skill permissão para compras, mensagens externas ou deploy que o usuário não autorizou.
Adicione exemplos pequenos e referências aos documentos do projeto; evite copiar o roadmap.
```

## Criar agentes de desenvolvimento (opcional) -> FEITO

Definições: [agentes-desenvolvimento.md](agentes-desenvolvimento.md) e skills `.cursor/skills/nexo-dev-*/`.

```text
Prepare definições portáveis de papéis (não execute agentes ainda): Implementador do ticket,
Revisor de isolamento, Avaliador de qualidade e Revisor de UX. Cada papel deve receber escopo,
arquivos permitidos, formato do relatório e evidências exigidas. Paralelizar apenas tarefas
sem conflito de escrita; revisão não concede permissão de deploy. O agente principal integra
resultados e executa testes. Não confundir esses papéis com os nós LangGraph do produto.
```

## MCPs de desenvolvimento

```text
Avalie se um MCP reduz trabalho real neste projeto antes de criar servidor customizado.
Proponha configuração de escopo mínimo para: docs oficiais, GitHub do repositório, banco
local de teste e browser de staging. Credenciais vêm de variáveis/secret manager, nunca JSON
versionado. Banco de produção fica excluído. Servidor SQL deve ser read-only e restrito a
fixtures. Se justificar MCP customizado, defina ferramentas tipadas de catálogo/evals sem
SQL arbitrário, autenticação, rate limit, logs redigidos e testes de abuso. Não instalar,
conectar conta externa ou expor porta pública automaticamente.
```

## Pesquisa e conteúdo

```text
Leia docs/lancamento.md e docs/custos.md. Prepare três peças da semana atual usando apenas
capacidades realmente demonstradas. Separe resultados medidos de hipóteses. Não mencionar
nome/dados de cliente sem consentimento. Entregue textos e roteiro de demo para revisão;
não publique, envie mensagens nem ative anúncios. Revise preços e políticas em fontes oficiais
antes de apresentar números como atuais.
```

## Sequência de execução: Setup

INF-001 → BE-001 → BE-002 → BE-003 → FE-001 → INF-002

## Sequência de execução: MVP

BE-004 → BE-005 → BE-006 → BE-007 → BE-008 → BE-009 → BE-010 → BE-011 → FE-002 → FE-003 → BE-012 → FE-004 → BE-013 → INF-003 → QA-001 → GT-001

## Sequência de execução: v1

BE-014 → BE-015 → FE-005 → BE-016 → BE-017 → FE-006 → BE-018 → FE-007 → BE-019 → QA-002

## Sequência de execução: v2

BE-020 → BE-021 → BE-022 → FE-008 → QA-003 → GT-002
