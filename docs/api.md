# Contratos e cobertura da API

Base `/v1`. Bearer JWT + `X-Tenant-ID` e membership em todas rotas privadas, salvo lista das
próprias organizações. Papéis: viewer lê; analyst consulta/cria conteúdo; admin gerencia
fontes/regras/membros; owner gerencia cobrança e exclusão. O boilerplate agrupa owner/admin/
analyst como editores; granularidade final é BE-002 e FE-007.

| Entidade | Rotas desejadas | Entregue / ticket |
|---|---|---|
| Tenant | GET /me/organizations; POST /organizations; GET/PATCH /organizations/{id} | GET entregue; BE-001 |
| Membership | GET/POST /members; PATCH/DELETE /members/{id} | FE-007 + BE-002 |
| Source | GET/POST /sources; GET/PATCH/DELETE /sources/{id}; POST /sources/{id}/test | GET/POST metadados entregues; BE-004/014/016 |
| SyncRun | POST /sources/{id}/sync; GET /sources/{id}/runs; GET /runs/{id} | BE-005/015; Idempotency-Key |
| Dataset | GET /datasets; GET /datasets/{id}/catalog; GET /datasets/{id}/versions | BE-005 |
| SemanticRule | GET/POST /rules; POST /rules/{id}/approve; POST /rules/{id}/retire | BE-006; aprovação admin |
| Conversation | GET/POST /conversations; GET/DELETE /conversations/{id} | BE-009; privado por usuário quando necessário |
| Message | GET /conversations/{id}/messages; POST /chat | POST /chat entregue, creates new conversation; BE-009 |
| QueryRun | GET /queries/{id}; GET /queries/{id}/evidence | BE-008/009; sem SQL executável vindo do cliente |
| Correction | POST /corrections; GET /corrections; POST /corrections/{id}/review | POST pendente entregue; BE-010 |
| Dashboard | GET/POST /dashboards; GET/PATCH/DELETE /dashboards/{id}; POST /dashboards/{id}/refresh | GET/POST metadados entregues; BE-012 |
| ReportSchedule | GET/POST /reports; PATCH/DELETE /reports/{id}; POST /reports/{id}/preview | BE-017 |
| Integration | GET /integrations; POST /integrations/{provider}/connect; DELETE /integrations/{id} | BE-014/017/020; DTO sem tokens |
| WebhookEvent | POST /webhooks/{provider}; GET /integrations/{id}/events | BE-018/020; assinatura substitui JWT no recebimento |
| Subscription | GET /billing; POST /billing/checkout; POST /billing/cancel | BE-018; owner |
| UsageEvent | GET /usage?from=&to= | BE-013; agregado por mês |
| AuditEvent | GET /audit?actor=&action=&from= | BE-003/019; somente admin/owner |

GET /health e /ready públicos para infraestrutura; ready testa conexão de banco.
Listas entregues usam offset/limit (máximo 100); evoluir cursor em volumes grandes.
Eventos de auditoria/uso/query não possuem edição pública. Exclusões de fonte e tenant são
jobs explícitos; usar soft delete para não quebrar proveniência, depois aplicar retenção.

Exemplo de resposta do chat na base atual:

```json
{"conversation_id":"uuid","message_id":"uuid","answer":"Conecte e sincronize uma fonte...","status":"needs_setup","trace":["catalog","clarify"]}
```

Erros: 401 sessão ausente/inválida; 403 associação/papel insuficiente; 404 recurso inacessível;
409 duplicação/conflito; 422 entrada inválida; 429 cota; 503 dependência indisponível.
Detalhes de validação contêm campo/mensagem, sem eco de credenciais enviadas.
