# Decisões recuperadas e ajustes

## Confirmado na conversa

- Python 3.12, FastAPI, SQLAlchemy 2 e Alembic; LangGraph para orquestração.
- Next.js 15, App Router, TypeScript, Tailwind e componentes compatíveis com shadcn/ui.
- PostgreSQL 16 + pgvector; Redis e worker. Escolha desta entrega: ARQ, pela simplicidade async.
- Supabase Auth com validação de JWT no backend.
- Docker em VPS; repositório novo, sem assumir acesso ao código Windy/Seedash.
- Cada organização com schema próprio para dados importados.
- MVP inicial e evolução até junho/2027, sem eliminar os módulos de WhatsApp e relatórios.
- Google Sheets, Excel/CSV, Postgres/MySQL somente leitura, Resend e cobrança brasileira.

## ADR-001 — Monolito modular
Contexto: um desenvolvedor e orçamento limitado. Decisão: API única, módulos separados,
worker em processo próprio. Consequência: deploy simples; escalar workers antes de separar serviços.

## ADR-002 — Plano de controle compartilhado, dados por schema
Contexto: custo e isolamento. Decisão: entidades operacionais em tabelas compartilhadas com
`tenant_id`; dados tabulares em `t_<uuid sem hífens>`. Consequência: schemas não são uma barreira
sozinhos. Produção requer roles restritas, teste de troca de tenant e RLS no plano de controle.
Nunca usar o usuário de migration para executar SQL gerado. O Compose atual é ambiente local.

## ADR-003 — Autenticação assimétrica
Contexto: Supabase controla sessões. Decisão: validar assinatura ES256/RS256 por JWKS,
issuer, audience, exp e sub; associação usuário × tenant vem do banco. Consequência:
header de tenant nunca concede acesso. Projetos legados HS256 precisam migrar chaves ou implementar
verificação remota explícita; não aceitar algoritmos arbitrários.

## ADR-004 — Correção é proposta, não verdade automática
Contexto: usuário ou atacante pode ensinar regra errada. Decisão: correção pendente,
aprovação por responsável e teste de regressão antes da ativação. Consequência:
aprendizado auditável e reversível; nenhuma promessa de nunca mais errar.

## ADR-005 — Um caminho analítico
Contexto: planilhas e bancos diferentes. Decisão: snapshots normalizados no PostgreSQL,
consultas sempre sobre versão publicada. Consequência: cópia e latência de atualização;
cliente vê data da última sincronização. Consulta federada fica fora do MVP.

## ADR-006 — Hospedagem comercial
Contexto: o plano anterior assumia Vercel gratuito para vender. Decisão: Next.js na mesma VPS
no piloto, ou plano comercial Vercel se escolhido. Consequência: considerar RAM, backup e proxy
na VPS. O Hobby é restrito a uso pessoal não comercial:
https://vercel.com/docs/plans/hobby (consultado em 28/10/2026).

## ADR-007 — Versões e atualizações
Contexto: a stack aprovada não fixa patches. Decisão: Next.js 15 com mínimo 15.5.28,
lockfile npm entregue e atualização controlada antes de produção. Consequência: manter a stack
e incorporar correções de segurança. Referência oficial:
https://nextjs.org/blog/nextjs-security-update-october-14-2026.
Python usa intervalos compatíveis nesta base; congelar lock com hashes no INF-001.

## Decisões a validar durante implementação

Nome Nexo é provisório; conferir marca/domínio antes de lançar. Asaas é a primeira opção de
billing, mas a conta e condições comerciais precisam ser validadas. Provedor/modelo de IA
será escolhido por avaliação de custo, latência e acurácia no BE-007; não depende de fine-tuning.
Capacidade semanal e datas são planejamento, não garantia. Meta inicial de cinco semanas é
um experimento com um único CSV e um cliente piloto, não todos os conectores prontos.
