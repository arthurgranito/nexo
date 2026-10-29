# MCPs de desenvolvimento — avaliação e escopo mínimo

Documento de **planejamento** para ferramentas MCP usadas **só na engenharia** do Nexo.
Não confundir com nós LangGraph do produto ([arquitetura.md](arquitetura.md)).
Nenhum servidor foi instalado nem conta externa conectada nesta entrega.

## Veredito

| Área | MCP reduz trabalho real? | Recomendação |
|------|--------------------------|--------------|
| Documentação oficial (Next, Supabase, FastAPI, pgvector) | **Sim, moderado** — evita copiar URLs desatualizadas e acelera ADR/custos | Fetch ou busca com **allowlist** de domínios; preferir pánicas oficiais |
| GitHub do repositório (`arthurgranito/nexo`) | **Sim** — PR, checks, issues sem sair do editor | MCP GitHub ou `gh` no terminal; token **somente leitura** via env |
| Banco local de teste (Compose) | **Parcial** — hoje pytest + Compose já cobrem RLS e tenants | **Não** expor SQL arbitrário; shell/`pytest` até BE-008+; MCP SQL só com role read-only + fixtures |
| Browser de staging | **Sim** — valida FE-001+ e fluxos em `flows.md` | MCP browser do Cursor contra `STAGING_BASE_URL`; login manual ou usuário de teste via secret manager |
| Servidor MCP **custom** Nexo | **Ainda não** — catálogo/evals maduros só após BE-005/BE-011 | Adiar; quando existir harness, ferramentas **tipadas** (catálogo/eval), sem SQL livre |

**Conclusão:** adotar MCP **genéricos** de escopo mínimo (docs, GitHub, browser) quando o humano autorizar a configuração local. **Não** criar servidor customizado antes do harness BE-011; até lá, skills `nexo-eval`, `nexo-connector` e testes pytest são a fonte de verdade.

## Princípios (alinhados a AGENTS.md)

1. Credenciais em variáveis de ambiente ou secret manager — **nunca** JSON de token no Git.
2. Banco de **produção** e URLs de staging/prod de clientes ficam **fora** de qualquer MCP.
3. SQL via MCP (se algum dia existir) = role analítica **read-only**, schemas de **fixture**, mesmas regras que o executor (BE-008).
4. Não instalar pacotes MCP, não conectar contas nem expor portas públicas **automaticamente** neste repositório.
5. Logs de ferramentas devem **redigir** DSN, JWT, chaves API e células identificáveis.

## Escopo mínimo por bloco

### 1. Documentação oficial

**Objetivo:** consultar políticas e APIs atuais (ex.: planos Vercel, security advisories Next, JWKS Supabase).

| Controle | Valor |
|----------|--------|
| Domínios permitidos (exemplo) | `nextjs.org`, `supabase.com`, `fastapi.tiangolo.com`, `www.postgresql.org`, `vercel.com`, `docs.github.com` |
| Negado | Domínios arbitrários do usuário, intranet de cliente, paste bins |
| Credenciais | Nenhuma para leitura pública |
| Alternativa sem MCP | `WebFetch` / busca manual + citação de URL e data em `docs/decisoes.md` |

### 2. GitHub do repositório

**Objetivo:** ler PR, comentários, status de CI, issues ligadas a tickets BE-/FE-.

| Controle | Valor |
|----------|--------|
| Repositório | Apenas `arthurgranito/nexo` (ou fork explícito do desenvolvedor) |
| Token | `GITHUB_TOKEN` ou `GH_TOKEN` no ambiente do usuário; escopo mínimo `repo` read ou fine-grained read em Contents + Pull requests + Actions |
| Negado | Escrita em main sem fluxo humano, fork de terceiros, orgs não relacionadas |
| Alternativa sem MCP | CLI `gh pr view`, `gh run list` (já previsto em regras de PR do projeto) |

### 3. Banco local de teste

**Objetivo:** inspecionar schema de fixture e depurar testes PG — **não** substituir migrations nem executar SQL de produto sem validador.

| Controle | Valor |
|----------|--------|
| Host permitido | `127.0.0.1` / `localhost` na porta publicada pelo [docker-compose.yml](../docker-compose.yml) (somente com stack local ativa) |
| Usuário | Preferir role `nexo_executor` ou role de teste read-only provisionada em fixtures — **nunca** `nexo` migrator |
| Database | `nexo` local; schemas `t_*` de tenants sintéticos criados por `app.seed` / testes |
| Negado | Hostnames de cloud, connection strings de `.env` de staging/prod, `COPY`, DDL, escrita, `pg_read_file`, extensões de rede |
| Fluxo preferido hoje | `docker compose up -d db` → `pytest backend/tests/test_rls_pg.py` |

Quando BE-011 existir, se MCP SQL for necessário, restringir a **consultas pré-aprovadas** ou views materializadas de fixture — ver seção “Servidor customizado”.

### 4. Browser de staging

**Objetivo:** smoke de login, seletor de organização e telas FE sem deploy local completo.

| Controle | Valor |
|----------|--------|
| URL base | `STAGING_BASE_URL` (ex.: `https://staging.example.com`) — variável local, não commitada |
| Auth | Supabase real; **sem** gravar senha no `mcp.json`; sessão iniciada pelo humano ou usuário de teste rotacionado |
| Negado | Produção de cliente, WhatsApp real, pagamentos Asaas reais |
| Ferramenta | MCP browser integrado ao Cursor (snapshot + interação); lock/unlock conforme documentação do servidor |

## Configuração de referência (não aplicada)

Arquivo exemplo versionado: [.cursor/mcp.json.example](../.cursor/mcp.json.example).
Copie para configuração **pessoal** do Cursor (User ou Project settings) e substitua placeholders por env vars **no SO**, não no repositório.

Variáveis típicas (documentação apenas):

| Variável | Uso |
|----------|-----|
| `GITHUB_TOKEN` | GitHub MCP / gh |
| `STAGING_BASE_URL` | Navegação browser |
| `NEXO_MCP_PG_DSN` | Opcional, futuro; deve apontar só para Postgres local read-only |
| `NEXO_MCP_API_KEY` | Futuro servidor custom; rotação manual |

## Servidor MCP customizado Nexo (somente se BE-011+ justificar)

**Gatilho:** harness de eval com dezenas de casos, necessidade de repetir “listar catálogo publicado + rodar caso N” sem colar SQL no chat.

**Ferramentas tipadas (proposta):**

| Ferramenta | Entrada | Saída | Proibido |
|------------|---------|-------|----------|
| `catalog_list_sources` | `tenant_fixture_id` (enum de fixtures) | IDs + `schema_version` + stale | SQL, outro tenant |
| `catalog_describe_table` | `source_id`, `table_name` | colunas, tipos, amostra mascarada | DDL, dados reais de cliente |
| `eval_list_cases` | filtro opcional por tag | lista de case_id sintéticos | — |
| `eval_run_case` | `case_id`, `model_profile` opcional | métricas + trace redigido | bypass do validador SQL |
| `eval_last_report` | `run_id` | acurácia, cobertura, p95 agregados | paths absolutos com secrets |

**Não expor:** `execute_sql(query: string)` ou equivalente.

**Operação:**

- Autenticação: API key local (`NEXO_MCP_API_KEY`) ou mTLS loopback.
- Rate limit: ex. 30 chamadas/min por sessão; eval_run_case conta no orçamento de eval.
- Logs: redação de DSN, JWT, e-mail, telefone; apenas IDs de tenant fixture.
- Testes de abuso (obrigatórios antes de habilitar): tenant B com fixture A; injection em `table_name`; path `../`; payload oversized; tentativa de second statement em parâmetros.

**Implementação:** ticket futuro dedicado (ex. INF-MCP ou anexo a BE-011), não parte do escopo atual.

## Relação com skills e agentes de desenvolvimento

| Artefato | Papel |
|----------|--------|
| [nexo-dev-implementer](../.cursor/skills/nexo-dev-implementer/SKILL.md) | Implementa tickets; MCP é acelerador opcional |
| [nexo-dev-isolation-reviewer](../.cursor/skills/nexo-dev-isolation-reviewer/SKILL.md) | Exige que qualquer MCP de dados respeite tenant/fixture |
| [nexo-dev-quality](../.cursor/skills/nexo-dev-quality/SKILL.md) | pytest/ruff permanecem gate; MCP não substitui CI |
| [nexo-eval](../.cursor/skills/nexo-eval/SKILL.md) | Fonte de contrato para ferramentas custom futuras |

## Checklist antes de ligar qualquer MCP (humano)

- [ ] Confirmou que DSN/host não é produção
- [ ] Token GitHub é read-only e revogável
- [ ] Allowlist de docs revisada
- [ ] Staging usa dados sintéticos
- [ ] Nenhum secret commitado
- [ ] Equipe sabe que MCP browser não substitui QA-001

## Próximo ticket de produto

[INF-002](roadmap.md#inf-002--separar-configuração-local-staging-e-produção) — separação de ambientes, TLS em staging, `DEV_AUTH` bloqueado fora do local.
