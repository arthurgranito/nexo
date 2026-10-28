# Ingestão e sincronização

## Contrato comum

Cada conector implementa `discover`, `extract(checkpoint)`, `normalize`, `validate` e
`publish`. Payload do job só contém IDs; buscar secrets no backend por referência. Nunca
colocar senha, refresh token ou conteúdo da planilha no Redis/log. Uma fonte tem no máximo
uma sincronização ativa. Chave idempotente = tenant + source + versão remota/conteúdo.

Pipeline: pending → running → staged → validated → published; erro → failed, mantendo a
última versão publicada intacta. Guardar início/fim UTC, watermark anterior/novo, hash,
linhas lidas/escritas/rejeitadas, mudanças de schema e código do erro. A versão só fica
disponível depois do commit; consultas em andamento continuam usando versão consistente.

## CSV/Excel (primeiro conector)

1. Upload com limite inicial de 10MB/50 mil linhas; MIME, extensão e conteúdo validados.
2. CSV: detectar delimitador e encoding com confirmação; Excel: listar abas e selecionar.
3. Prévia com 20 linhas mascaradas; usuário escolhe cabeçalho, tipos, chaves e moeda.
4. Normalizar espaços, nomes duplicados, datas com locale explícito, decimal com vírgula,
   células vazias e fórmulas. Não executar macros/fórmulas; exigir valores calculados ou
   sinalizar células sem cache. Campos originais preservados no staging restrito.
5. Validar colunas obrigatórias, linhas rejeitadas e totais de controle.
6. Publicar snapshot e catálogo na mesma transação; hash igual torna reenvio no-op.
7. Excel exportado para relatórios deve neutralizar formula injection (`=`, `+`, `-`, `@`).

Sem chave de negócio confiável, substituir snapshot completo. Não inventar upsert por
posição da linha; usuário pode reordenar planilhas. Não inferir exclusão silenciosamente.

## Google Sheets

OAuth por organização, `state` único com TTL e vinculado à sessão, callback com allowlist,
escopos mínimos readonly e refresh token criptografado fora do browser. Não exigir tornar
planilha pública. Permitir escolher arquivo/abas/intervalos e respeitar quota por projeto.

MVP: polling configurável de 15 minutos e “sincronizar agora”. Comparar hash de valores
normalizados para evitar publicar conteúdo igual; usar batch reads e backoff em 429/5xx,
até cinco tentativas com jitter. 401/403 interrompe loop e pede reconexão.

Apps Script é melhoria opcional, não garantia de atualização instantânea: `onEdit` não cobre
todas as mudanças feitas por API, fórmulas e outras automações. Webhook é sinal para
agendar sync, não transporte confiável de todo o conteúdo. Validar HMAC sobre corpo bruto,
timestamp, nonce e replay; debounce por fonte e manter polling reconciliador.

Fontes oficiais a conferir na implementação:
https://developers.google.com/workspace/sheets/api/limits
https://developers.google.com/apps-script/guides/triggers
https://developers.google.com/identity/protocols/oauth2/web-server

## Postgres/MySQL

Credencial criada pelo cliente com SELECT somente em views/tabelas autorizadas; TLS e
rotação. Validar destino contra SSRF, bloqueando metadata endpoints e rede interna não
autorizada. Conexões privadas devem ser provisionadas por operador, não liberadas por URL
arbitrária. Não extrair todas as bases automaticamente; usuário confirma allowlist.

Inicial: snapshot por tabela, timeout e tamanho máximo. Incremental só com chave estável
e cursor monotônico (`updated_at` + PK), janela de sobreposição e deduplicação. Deletes
precisam tombstones, CDC ou reconciliação periódica; `updated_at` sozinho não os detecta.

## Mudança de schema

Adicionar coluna nullable: sugerir nova versão. Remover/renomear/alterar tipo usado por
métrica: bloquear publicação automática, mostrar diff, pedir revisão de regras e gráficos.
Invalidar cache por `(tenant, dataset_version, semantic_version, filtros)`. Exibir no chat
hora de atualização, origem e aviso se ultrapassar SLA configurado. Nunca apresentar dados
de ontem como “agora” sem aviso.

## Operação

Fila com backpressure e cotas por tenant; retentativa apenas de erros transitórios.
Advisory lock ou lease com expiração; worker morto permite retomar sem duplicar publicação.
Outbox transacional agenda eventos após commit. Métricas: lag, duração, falhas, linhas,
schema drift, retries e fontes expiradas. Testes: duplicado, fora de ordem, edição concorrente,
revogação OAuth, worker morto antes/depois de commit e exclusão de linha.
