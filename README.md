# Nexo — assistente empresarial orientado a evidências

Nome de trabalho; disponibilidade de marca e domínio não foi verificada.
Pacote retomado da conversa “Criar software e ganhar dinheiro”, em 28/10/2026.

## Comece aqui

1. Leia [INICIO.md](INICIO.md): execução e limites da entrega.
2. Leia [docs/roadmap.md](docs/roadmap.md): tickets Setup → MVP → v1 → v2.
3. Use [docs/prompts.md](docs/prompts.md) para implementar uma fase por vez.

## Documentos

- [Arquitetura e agentes](docs/arquitetura.md)
- [Sincronização e conectores](docs/sincronizacao.md)
- [Modelo de dados](docs/modelagem.md)
- [Contratos da API](docs/api.md)
- [Custos e limites de investimento](docs/custos.md)
- [Lançamento, conteúdo e anúncios](docs/lancamento.md)
- [Operação e deploy](docs/operacao.md)
- [Decisões e pendências](docs/decisoes.md)
- [Verificação executada](docs/validacao.md)

## Estado real

Boilerplate funcional de infraestrutura e controle: cadastro/listagem de fontes, autenticação,
autorização por organização, gravação de conversas e propostas de correção, metadados de
dashboards, migração e worker com heartbeat. A interface permite testar o cadastro e o chat.

O chat retorna explicitamente `needs_setup`. Não existe ainda geração/execução de SQL por IA,
importador, OAuth Sheets, gráficos com dados reais, cobrança, relatórios ou WhatsApp.
Esses recursos estão especificados em tickets e prompts. Isso corresponde à entrega de
roadmap + boilerplate pedida no Claude, e não representa um produto completo pronto para vender.
