# Roadmap executável

## Objetivo e escopo

Assistente empresarial que entende fontes autorizadas, pergunta regras de negócio, responde
com evidências, gera dashboards e aprende por correções aprovadas. Evolui para sincronização,
relatórios, cobrança e atendimento WhatsApp com análise interna das conversas.

Artefatos de infraestrutura/modelos já estão no repositório. Os tickets abaixo implementam
os recursos do produto; não representam funções já concluídas. O desenvolvimento é do zero:
a experiência Windy/Seedash informa o desenho, mas nenhum código desses projetos foi acessado.

## Calendário de referência

| Fase | Janela proposta | Resultado e gate |
|---|---|---|
| Setup | 29/10–08/11/2026 | autenticação, isolamento real, CI, staging |
| MVP | 09/11–06/12/2026 | CSV + chat verificável + dashboard + correção + piloto |
| v1 | dez/2026–fev/2027 | Sheets, DBs, relatórios e cobrança operáveis |
| v2 | mar–mai/2027 | WhatsApp, inbox e análise de conversas |
| Consolidação | jun/2027 | suporte, rentabilidade e confiabilidade |

Estimativas P=até 4h, M=4–12h, G=12–24h, sujeitas a revisão após Setup. Somadas, as tarefas
ultrapassam um MVP completo de cinco semanas a 10h/semana. Para validar em cinco semanas,
limitar o piloto a um CSV, poucas métricas e acompanhamento manual; retirar da janela inicial
Sheets, SQL externo, billing automático e WhatsApp. Se os gates não passarem, adiar a venda,
sem trocar verificação por prazo. A data comercial é meta de planejamento, não compromisso.

## Modelagem e contratos

Todos os campos, constraints, índices e relações estão em [modelagem.md](modelagem.md),
com diagrama ER. Contratos e rotas estão em [api.md](api.md). Políticas de agentes e sincronização
estão em [arquitetura.md](arquitetura.md) e [sincronizacao.md](sincronizacao.md).

## Tickets

## Setup

### INF-001 — Congelar dependências e configurar ambientes

- **Descrição:** Congelar dependências e configurar ambientes, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** infra.
- **Arquivos:** `backend/pyproject.toml; frontend/package-lock.json; .github/workflows/ci.yml`.
- **Dependências:** —.
- **Critérios de aceite:** Instalação limpa reproduzível; lock Python com hashes; CI lint/test/build; nenhum segredo no Git.
- **Esforço:** M.
- **Atenção técnica:** Não copiar patches antigos; revisar advisories antes de travar versões.

### BE-001 — Provisionar tenant e papéis no PostgreSQL

- **Descrição:** Provisionar tenant e papéis no PostgreSQL, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/tenancy.py; backend/migrations/versions/0002_roles.py`.
- **Dependências:** INF-001.
- **Critérios de aceite:** Criar tenant + membership + schema em transação; role analítica sem acesso aos tenants vizinhos; rollback em falha.
- **Esforço:** G.
- **Atenção técnica:** Schema sozinho não isola; separar usuário migrator, API e executor.

### BE-002 — Completar sessão Supabase e autorização

- **Descrição:** Completar sessão Supabase e autorização, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/auth.py; backend/tests/test_auth.py`.
- **Dependências:** BE-001.
- **Critérios de aceite:** JWT válido/expirado/issuer errado testados; owner/admin/analyst/viewer respeitados; revogação de membership efetiva.
- **Esforço:** M.
- **Atenção técnica:** Não usar service role no cliente; JWKS cache e rotação testados.

### BE-003 — Aplicar RLS e repositórios com escopo

- **Descrição:** Aplicar RLS e repositórios com escopo, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/repositories.py; backend/migrations/versions/0003_rls.py`.
- **Dependências:** BE-001.
- **Critérios de aceite:** Todas tabelas de controle com política fail-closed; teste por conexão real tenta ler/escrever outro tenant e falha.
- **Esforço:** G.
- **Atenção técnica:** Roles proprietárias e BYPASSRLS burlam políticas; testar API sem ownership.

### FE-001 — Criar login, logout e seletor de organização

- **Descrição:** Criar login, logout e seletor de organização, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/login/page.tsx; frontend/lib/supabase.ts; frontend/app/app/layout.tsx`.
- **Dependências:** BE-002.
- **Critérios de aceite:** Login real sem colar token; sessão expira corretamente; troca de organização invalida cache e histórico.
- **Esforço:** M.
- **Atenção técnica:** Cookies/CSRF conforme modelo escolhido; nunca confiar em route guard do frontend.

### INF-002 — Separar configuração local, staging e produção

- **Descrição:** Separar configuração local, staging e produção, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** infra.
- **Arquivos:** `docker-compose.production.yml; deploy/Caddyfile; backend/app/config.py`.
- **Dependências:** INF-001.
- **Critérios de aceite:** DEV_AUTH rejeitado fora do local; TLS no staging; banco/Redis privados; healthcheck e logs sem secrets.
- **Esforço:** M.
- **Atenção técnica:** Não expor Compose local diretamente na Internet.

## MVP

### BE-004 — Implementar upload CSV/Excel com prévia

- **Descrição:** Implementar upload CSV/Excel com prévia, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/connectors/files.py; backend/app/routes/uploads.py`.
- **Dependências:** BE-003.
- **Critérios de aceite:** Arquivo <=10MB; cabeçalho/tipos aprovados; erro por linha; rejeitar macro/arquivo inválido; prévia não publica dados.
- **Esforço:** G.
- **Atenção técnica:** Locale de moeda/data e fórmulas sem cache exigem revisão.

### BE-005 — Publicar snapshot e catálogo versionados

- **Descrição:** Publicar snapshot e catálogo versionados, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/ingestion.py; backend/app/worker.py; backend/app/catalog.py`.
- **Dependências:** BE-004.
- **Critérios de aceite:** Hash repetido é no-op; falha deixa versão anterior; dataset e catálogo publicados juntos; fonte mostra ready/failed.
- **Esforço:** G.
- **Atenção técnica:** Staging e tabela final sempre dentro do schema autorizado.

### BE-006 — Implementar entrevista e regras semânticas

- **Descrição:** Implementar entrevista e regras semânticas, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/semantics.py; backend/app/routes/rules.py`.
- **Dependências:** BE-005.
- **Critérios de aceite:** Perguntar conceito de venda, devolução, moeda e período; estados pending/approved/retired; aprovação auditada.
- **Esforço:** M.
- **Atenção técnica:** Não tratar nome de coluna como regra de negócio.

### BE-007 — Escolher modelo e implementar plano estruturado

- **Descrição:** Escolher modelo e implementar plano estruturado, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/llm.py; backend/app/agents.py; evals/cases.jsonl`.
- **Dependências:** BE-006.
- **Critérios de aceite:** Comparar dois modelos com mesmo conjunto; schema Pydantic validado; timeout, budget e max 2 tentativas; perguntas ambíguas abstêm.
- **Esforço:** G.
- **Atenção técnica:** Catálogo/amostra são dados não confiáveis; minimizar envio e registrar custo.

### BE-008 — Construir validador e executor SQL restrito

- **Descrição:** Construir validador e executor SQL restrito, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/sql_guard.py; backend/app/executor.py; backend/tests/test_executor_pg.py`.
- **Dependências:** BE-003, BE-007.
- **Critérios de aceite:** AST allowlist; transação read-only; timeout; LIMIT; acesso cruzado, SQL injection e função perigosa bloqueados no PostgreSQL real.
- **Esforço:** G.
- **Atenção técnica:** EXPLAIN e cotas evitam consultas agregadas excessivamente caras.

### BE-009 — Responder com proveniência e verificações

- **Descrição:** Responder com proveniência e verificações, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/agents.py; backend/app/routes/chat.py`.
- **Dependências:** BE-008.
- **Critérios de aceite:** Resposta contém query_id, versão, fonte e updated_at; totais vêm do resultado; vazio/erro/stale têm estados distintos.
- **Esforço:** G.
- **Atenção técnica:** Não permitir que apresentador invente números ou esconda limitação.

### BE-010 — Criar memória de correção aprovada

- **Descrição:** Criar memória de correção aprovada, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/memory.py; backend/app/routes/corrections.py`.
- **Dependências:** BE-009.
- **Critérios de aceite:** Correção vira proposta; admin aprova após regressão; regra conflitante exige revisão; rollback versionado.
- **Esforço:** G.
- **Atenção técnica:** Feedback não é fine-tuning automático; isolar retrieval por tenant.

### BE-011 — Entregar harness de avaliação

- **Descrição:** Entregar harness de avaliação, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/evals.py; evals/cases.jsonl; evals/report.py`.
- **Dependências:** BE-010.
- **Critérios de aceite:** >=60 casos com gabarito; métricas acurácia/cobertura/erro confiante/latência/custo; relatório por versão e falhas reproduzíveis.
- **Esforço:** M.
- **Atenção técnica:** Separar exemplos de desenvolvimento e holdout; não alegar 100% fora do conjunto.

### FE-002 — Criar wizard de importação e contexto

- **Descrição:** Criar wizard de importação e contexto, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/sources/page.tsx; frontend/components/source-wizard.tsx`.
- **Dependências:** BE-004, BE-006, FE-001.
- **Critérios de aceite:** Preview, mapeamento, erros por linha, progresso, retry e data da publicação visíveis; funciona em celular.
- **Esforço:** G.
- **Atenção técnica:** Upload cancelado não pode aparecer ready.

### FE-003 — Criar chat com histórico, evidências e feedback

- **Descrição:** Criar chat com histórico, evidências e feedback, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/chat/page.tsx; frontend/components/evidence.tsx`.
- **Dependências:** BE-009, FE-001.
- **Critérios de aceite:** Conversa preserva contexto autorizado; mostra abstenção, fonte, SQL opcional e atualização; correção sem ativação imediata.
- **Esforço:** G.
- **Atenção técnica:** Abortar request não confirma cancelamento de job; proteger histórico por usuário/tenant.

### BE-012 — Gerar e salvar dashboards com spec restrita

- **Descrição:** Gerar e salvar dashboards com spec restrita, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/charts.py; backend/app/routes/dashboards.py`.
- **Dependências:** BE-009.
- **Critérios de aceite:** Tabela/barra/linha/KPI; spec referencia query validada do mesmo tenant; sem JS/HTML arbitrário; stale quando regra muda.
- **Esforço:** M.
- **Atenção técnica:** Não persistir SQL vindo livremente do browser.

### FE-004 — Renderizar dashboard e estados vazios

- **Descrição:** Renderizar dashboard e estados vazios, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/dashboards/page.tsx; frontend/components/chart.tsx`.
- **Dependências:** BE-012, FE-003.
- **Critérios de aceite:** Salvar pelo chat; filtros validados; sem dados fictícios em produção; unidades e datas visíveis; acessibilidade básica.
- **Esforço:** M.
- **Atenção técnica:** Gráfico não pode inverter escala/unidade ou agregar novamente no browser.

### BE-013 — Adicionar quotas e rate limiting compartilhado

- **Descrição:** Adicionar quotas e rate limiting compartilhado, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/limits.py; backend/app/middleware.py`.
- **Dependências:** BE-009.
- **Critérios de aceite:** Limite por usuário/tenant; 429 e Retry-After; limite de custo reservado antes da chamada; atomicidade no Redis.
- **Esforço:** M.
- **Atenção técnica:** Processos múltiplos tornam contador em memória insuficiente.

### INF-003 — Monitorar e testar restauração do piloto

- **Descrição:** Monitorar e testar restauração do piloto, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** infra.
- **Arquivos:** `deploy/backup.sh; deploy/restore.md; backend/app/telemetry.py`.
- **Dependências:** INF-002, BE-005.
- **Critérios de aceite:** Backup cifrado fora da VPS; restore em staging verificado; alertas em erro/lag/custo; logs por request_id sem conteúdo sensível.
- **Esforço:** G.
- **Atenção técnica:** Snapshot no mesmo disco não protege contra perda da VPS.

### QA-001 — Validar ponta a ponta e isolamento com dois tenants

- **Descrição:** Validar ponta a ponta e isolamento com dois tenants, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** qualidade.
- **Arquivos:** `tests/e2e/pilot.spec.ts; backend/tests/test_tenancy_pg.py`.
- **Dependências:** FE-004, BE-011, BE-013, INF-003.
- **Critérios de aceite:** Upload→entrevista→chat→gráfico→correção; viewer não edita; zero acesso cruzado; gate de qualidade documentado.
- **Esforço:** G.
- **Atenção técnica:** Não liberar piloto pago com isolamento ou restauração pendentes.

### GT-001 — Executar piloto acompanhado e oferta de implantação

- **Descrição:** Executar piloto acompanhado e oferta de implantação, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** comercial.
- **Arquivos:** `docs/piloto.md; docs/lancamento.md`.
- **Dependências:** QA-001.
- **Critérios de aceite:** Cliente confirma 3 perguntas úteis, regras e aceite; proposta com escopo e limites; primeira entrega observada.
- **Esforço:** M.
- **Atenção técnica:** Não presumir contato/permissão da Pró Abelha; só abordar por ação humana autorizada.

## v1

### BE-014 — Conectar Google Sheets por OAuth

- **Descrição:** Conectar Google Sheets por OAuth, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/connectors/google.py; backend/app/routes/oauth.py`.
- **Dependências:** QA-001.
- **Critérios de aceite:** State/TTL/sessão validados; token cifrado; scopes readonly; reconexão e revogação; abas explicitamente escolhidas.
- **Esforço:** G.
- **Atenção técnica:** Evitar planilha pública e vazamento de refresh token.

### BE-015 — Sincronizar Sheets com reconciliação e schema drift

- **Descrição:** Sincronizar Sheets com reconciliação e schema drift, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/sync.py; backend/app/worker.py`.
- **Dependências:** BE-014, BE-005.
- **Critérios de aceite:** Polling 15min, botão manual, retries jitter; hash no-op; schema incompatível bloqueia publicação; delete refletido no snapshot.
- **Esforço:** G.
- **Atenção técnica:** onEdit não captura toda atualização; webhook é melhoria opcional.

### FE-005 — Gerenciar conectores e saúde das fontes

- **Descrição:** Gerenciar conectores e saúde das fontes, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/sources/[id]/page.tsx`.
- **Dependências:** BE-015, FE-002.
- **Critérios de aceite:** Última sync, próxima sync, erros, diferenças de schema e reconexão; credencial nunca devolvida.
- **Esforço:** M.
- **Atenção técnica:** Data stale é sinalizada também no chat e dashboard.

### BE-016 — Adicionar Postgres/MySQL com allowlist

- **Descrição:** Adicionar Postgres/MySQL com allowlist, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/connectors/sql.py; backend/app/network_policy.py`.
- **Dependências:** BE-015.
- **Critérios de aceite:** SELECT readonly TLS; snapshot limitado; teste SSRF; incremental com watermark+PK; deletes reconciliados.
- **Esforço:** G.
- **Atenção técnica:** Acesso a redes privadas somente provisionado por operador.

### BE-017 — Agendar relatórios e envio Resend

- **Descrição:** Agendar relatórios e envio Resend, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/reports.py; backend/app/connectors/email.py`.
- **Dependências:** BE-012, BE-015.
- **Critérios de aceite:** Cron com timezone; preview; idempotência por período; somente destinatários aprovados; retry sem duplicar envio.
- **Esforço:** G.
- **Atenção técnica:** Mudança de fuso/horário de verão e dados stale precisam de política explícita.

### FE-006 — Criar tela de agendamentos

- **Descrição:** Criar tela de agendamentos, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/reports/page.tsx`.
- **Dependências:** BE-017.
- **Critérios de aceite:** Preview e confirmação do destinatário; editar/pausar; histórico de entrega; erros acionáveis.
- **Esforço:** M.
- **Atenção técnica:** Não enviar relatório no primeiro clique de preview.

### BE-018 — Integrar Asaas e assinaturas

- **Descrição:** Integrar Asaas e assinaturas, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/billing.py; backend/app/routes/billing.py`.
- **Dependências:** BE-013, QA-001.
- **Critérios de aceite:** Checkout sandbox; webhook autenticado e deduplicado; plano deriva do servidor; reconciliação; estados trial/active/past_due/canceled.
- **Esforço:** G.
- **Atenção técnica:** Nunca ativar conta com base no redirect do browser; não armazenar cartão.

### FE-007 — Criar administração, membros e faturamento

- **Descrição:** Criar administração, membros e faturamento, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/settings/page.tsx; frontend/app/app/billing/page.tsx`.
- **Dependências:** BE-018, BE-002.
- **Critérios de aceite:** Owner convida/remove papéis; viewer sem acesso financeiro; status e limites claros; auditoria administrativa.
- **Esforço:** G.
- **Atenção técnica:** Impedir remover último owner; convite expira e é de uso único.

### BE-019 — Adicionar exportação e retenção por organização

- **Descrição:** Adicionar exportação e retenção por organização, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/privacy.py; backend/app/routes/privacy.py`.
- **Dependências:** BE-018.
- **Critérios de aceite:** Exportação autenticada; job de exclusão com confirmação, prazo e auditoria; remover índices/memórias/secrets; documentar backup retention.
- **Esforço:** G.
- **Atenção técnica:** Definir controlador/operador e acordo com cliente antes de dados pessoais.

### QA-002 — Validar carga, backup e operação comercial

- **Descrição:** Validar carga, backup e operação comercial, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** qualidade.
- **Arquivos:** `tests/load/queries.py; docs/operacao.md`.
- **Dependências:** FE-007, BE-019, INF-003.
- **Critérios de aceite:** 10 tenants sintéticos; limites impedem noisy neighbor; restore por tenant ensaiado; rollback e suporte com runbook.
- **Esforço:** G.
- **Atenção técnica:** Escalar por carga medida, não por quantidade de agentes.

## v2

### BE-020 — Receber eventos oficiais WhatsApp

- **Descrição:** Receber eventos oficiais WhatsApp, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/connectors/whatsapp.py; backend/app/routes/whatsapp.py`.
- **Dependências:** QA-002.
- **Critérios de aceite:** Verificação challenge e assinatura do corpo bruto; dedupe por message_id; fila e identificação do tenant sem confiar no payload livre.
- **Esforço:** G.
- **Atenção técnica:** Conferir política Meta, consentimento e preço vigente antes da ativação.

### BE-021 — Criar atendimento externo com permissões próprias

- **Descrição:** Criar atendimento externo com permissões próprias, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/customer_agent.py; backend/app/customer_identity.py`.
- **Dependências:** BE-020.
- **Critérios de aceite:** Ferramentas públicas allowlist; pedido apenas do cliente verificado; handoff humano; opt-out; sem métricas internas.
- **Esforço:** G.
- **Atenção técnica:** Prompt injection não pode conceder ferramenta ou dado interno.

### BE-022 — Indexar conversas para análise interna

- **Descrição:** Indexar conversas para análise interna, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** backend.
- **Arquivos:** `backend/app/conversation_analytics.py`.
- **Dependências:** BE-021.
- **Critérios de aceite:** Retenção e mascaramento; usuário interno autorizado; busca por tenant; métricas distinguem mensagem, conversa e cliente.
- **Esforço:** G.
- **Atenção técnica:** Texto do cliente externo não é instrução confiável nem regra semântica.

### FE-008 — Entregar inbox e análises de conversas

- **Descrição:** Entregar inbox e análises de conversas, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** frontend.
- **Arquivos:** `frontend/app/app/inbox/page.tsx; frontend/app/app/analytics/page.tsx`.
- **Dependências:** BE-022.
- **Critérios de aceite:** Transferência bot↔humano; histórico, filtros e resumo com citações; logs de quem respondeu; opt-out visível.
- **Esforço:** G.
- **Atenção técnica:** Evitar resposta dupla durante handoff e jobs atrasados.

### QA-003 — Validar atendimento adversarial e lançamento ampliado

- **Descrição:** Validar atendimento adversarial e lançamento ampliado, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** qualidade.
- **Arquivos:** `tests/e2e/whatsapp.spec.ts; evals/customer_cases.jsonl`.
- **Dependências:** FE-008.
- **Critérios de aceite:** Cenários de pedido alheio, mensagem duplicada, jailbreak, opt-out, janela expirada e handoff passam; rollout por tenant.
- **Esforço:** G.
- **Atenção técnica:** WhatsApp não pode ser ativado globalmente antes do aceite e sandbox.

### GT-002 — Escalar aquisição com estudos de caso

- **Descrição:** Escalar aquisição com estudos de caso, respeitando os contratos e regras do documento de arquitetura. O objetivo é liberar a capacidade descrita no aceite sem abrir acesso entre organizações.
- **Camada:** comercial.
- **Arquivos:** `docs/lancamento.md; docs/custos.md`.
- **Dependências:** QA-003, GT-001.
- **Critérios de aceite:** Caso autorizado e mensurado; custo por lead e conversão medidos; mídia limitada à verba aprovada.
- **Esforço:** M.
- **Atenção técnica:** Nenhuma promessa de receita ou acurácia universal.

## Regras transversais de aceite

Cada endpoint mutável valida DTO, papel e tenant no servidor; detalhe inexistente e de outro
tenant retornam 404 indistinguíveis. Listas usam limite <=100, ordenação estável e filtros
allowlist. Erros padronizados como `error.code`, `detail`, `request_id`; nunca retornar secrets.
Criar testes de negócio e de falha, além do caminho feliz. Não escrever testes que apenas
espelham a implementação.

Backend: testes unitários para normalização/regras; integração com PostgreSQL/Redis para
RLS, roles, migrations, idempotência e concorrência; avaliação com gabarito para IA.
Frontend: validação de estados vazio/loading/erro/stale/abstention, teclado e celular.
E2E: dois tenants, usuário viewer, arquivos malformados, fonte revogada e custos esgotados.

Estado do frontend: Supabase para sessão; cache de servidor por tenant/usuário/filtros/versão,
com invalidação na troca de organização. Estado local para formulários e preview. SSE pode
ser adicionado no chat com request_id e cancelamento documentado; JSON síncrono é suficiente
no primeiro caminho vertical. Nunca guardar token em localStorage manualmente.

Logs estruturados por request_id/job_id/tenant_id pseudonimizado, sem prompts/dados brutos
por padrão. Métricas de p95, falhas, abstention, sync lag, filas, custo e quota. Alarmes
acionáveis para falha de backup, gasto acima da cota e fonte sem atualizar.

## Riscos e mitigação

1. Semântica errada com SQL válido: entrevista, regras aprovadas e gabarito do cliente.
2. Vazamento entre clientes: roles e RLS reais, testes adversariais e segredo fora do contexto.
3. Planilha bagunçada: preview, normalização determinística e revisão antes da publicação.
4. Custo de IA imprevisível: budget por pergunta/mês, contexto mínimo, cache versionado e cotas.
5. Prazo de um dev: caminho vertical pequeno e venda assistida somente após gates.
6. Correção contaminada: aprovação, regressão, versão e rollback.
7. Conectores instáveis: snapshots consistentes, retries e reconciliação, sem promessa de tempo real.
8. Dependência de fornecedores: adapters e exportação; monitorar quota/preço e termos.

## Ordem recomendada

INF-001 → BE-001/002/003 → FE-001/INF-002 → BE-004/005/006 → FE-002 →
BE-007/008/009 → FE-003 → BE-010/011/012/013 → FE-004/INF-003 → QA-001 → GT-001.
Depois BE-014/015/016, FE-005, BE-017/018, FE-006/007, BE-019 e QA-002.
Por fim BE-020/021/022, FE-008, QA-003 e GT-002.

Decisões ADR e consequências estão em [decisoes.md](decisoes.md). Ao concluir cada ticket,
anotar commit, checks executados e limitações numa seção de progresso; não marcar uma fase
como pronta só porque o código compila.
