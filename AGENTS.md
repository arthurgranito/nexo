# Instruções do projeto Nexo

Leia README.md, docs/decisoes.md, docs/arquitetura.md e o ticket solicitado antes de editar.
Implemente um caminho vertical por vez. O arquivo docs/roadmap.md é plano, não evidência de conclusão.
Não afirmar que conector, IA ou cobrança está implementado quando só existe um stub.
Preserve TypeScript strict, DTOs extra=forbid e validação no backend.
Todo recurso deve derivar tenant da membership autenticada; testar acesso cruzado.
Não enviar dados reais a modelos durante desenvolvimento; use fixtures sintéticas.
Nunca inserir chaves no Git, no frontend, em screenshots ou em logs.
SQL gerado só pode executar após validação determinística e com role analítica read-only.
Correção é proposta até aprovação e regressão. Não prometer 100% de acurácia.
Antes de encerrar: lint, testes relevantes, typecheck/build se frontend e atualizar progresso.
Se algum check não puder executar, informar exatamente o que ficou sem validação.
Não publicar, comprar, criar contas ou enviar mensagens para clientes sem autorização humana.
Não criar MCP server ou subagentes por padrão; justificar benefício e delimitar permissões.
