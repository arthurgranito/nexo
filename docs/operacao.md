# Operação e deploy

## Ambientes

Development: Compose local e auth demo opcional. Staging: Supabase real, dados sintéticos,
domínio HTTPS e DEV_AUTH=false. Production: credenciais distintas, roles restritas,
backup externo, cotas e alertas. Settings por ambiente são selecionados por ENVIRONMENT;
secrets pertencem ao ambiente, nunca à imagem Docker.

## Antes do primeiro cliente

1. Concluir BE-001/002/003 e testar com dois tenants no PostgreSQL, não só SQLite.
2. Criar usuário real no Supabase e membership por fluxo administrativo auditado.
3. Separar migrator, API e executor; aplicar RLS e revogar acesso indevido.
4. Definir domínio/TLS via proxy, origem CORS exata e política de sessão.
5. Configurar quota de modelo, tamanho de upload e concorrência por organização.
6. Backup criptografado diário externo; ensaiar restore e medir RPO/RTO.
7. Definir retenção, acesso de suporte e acordo de tratamento de dados com cliente.
8. Rodar avaliação, E2E e validação do dono das regras; habilitar um tenant por vez.

## Deploy proposto (INF-002/003)

Construir imagens por commit, armazenar em registry privado, executar migration com role
temporária dedicada antes do rollout. Usar estratégia expand/contract para alterações
destrutivas: adicionar, migrar dados, trocar leitura e só depois remover. Healthchecks de
API e worker antes de liberar tráfego. A migration inicial tem DDL explícito congelado;
mudanças posteriores exigem novas revisions, sem reescrever o histórico aplicado.

O Compose entregue é local, sem TLS ou configuração final de roles. Não é manifesto de
produção. O INF-002 produz override/proxy e separação de secrets conforme ambiente escolhido.

## Backup e recuperação

Meta proposta de piloto: RPO <=24h e RTO <=4h; confirmar com cliente e capacidade real.
Banco, arquivos originais/staging retidos, secrets e catálogo precisam política consistente.
Guardar backup fora da VPS e testar restore em instância descartável mensalmente.
Restore por tenant exige preservar referências do plano de controle ao schema importado.
Não declarar backup pronto apenas porque `pg_dump` terminou; verificar contagens e consulta.

## Incidentes

Fonte com falha: manter última versão, marcar stale, parar retries em credencial inválida.
Custo alto: bloquear novas chamadas do tenant e investigar nó/contexto; não remover cotas.
Vazamento suspeito: desabilitar tenant/integração afetada, preservar auditoria mínima,
revogar credenciais pertinentes e investigar escopo. Comunicação externa é humana.
Falha de deploy: reverter imagem; migration reversa só se segura e testada, senão fix forward.

## Checks de segurança associados ao trabalho

Injection: AST e parâmetros + role read-only. Auth: JWT validado e membership no servidor.
Dados sensíveis: secrets por referência e logs redigidos. Upload: tamanho/conteúdo/quota.
SSRF: conectores com allowlist e bloqueio de metadata. CORS: origens exatas. Rate limit:
Redis por tenant/usuário. CSRF: proteção compatível com sessão/cookie adotada. Dependências:
lockfiles e revisão de advisories. Tudo deve ter evidência em teste antes do gate comercial.
