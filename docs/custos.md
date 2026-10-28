# Orçamento e controle de gasto

Data de planejamento: 28/10/2026. Valores em reais abaixo são **envelopes de orçamento**,
não cotações de fornecedor ou promessa de retorno. Impostos, taxas de câmbio e tarifas
podem alterar o desembolso. Não houve compra nem contratação nesta entrega.

## Caixa inicial de R$2.000

| Uso | Teto reservado | Gatilho |
|---|---:|---|
| Prototipação/API de IA | R$150 | medição com dados sintéticos e limites por dia |
| Domínio | R$60 | após nome e interesse inicial validados |
| VPS + backup inicial | R$180 | apenas quando staging/piloto precisar estar online |
| Teste de aquisição | R$100 | após oferta e demo converterem organicamente |
| Reserva operacional | R$1.510 | não gastar antes de receita ou decisão explícita |
| Total | R$2.000 | desembolso pré-receita alvo <= R$490 |

Os R$490 são teto de experimento. Se o fornecedor não couber, adiar contratação ou rever
o plano; não consumir a reserva automaticamente. Assinaturas Claude/Cursor/Codex existentes
não estão incluídas: registre seu custo real e não assuma créditos ilimitados.

## Por fase

| Fase | Desembolso incremental planejado | Recorrência mensal planejada | Condição |
|---|---:|---:|---|
| Setup local | R$0–50 | R$0 | sem infraestrutura pública |
| MVP/avaliação | R$50–150 | R$0–100 IA | limitar contexto e rodadas |
| Piloto hospedado | R$100–290 | R$80–250 | VPS/backup/domínio conforme cotação |
| v1 | financiado por implantação | R$150–500 + taxas | só ativar recursos demandados |
| v2 | financiado por receita | base + mensagens/modelos | orçamento por tenant e volume |

Faixas não devem ser somadas como se fossem preços confirmados; há sobreposição entre
reserva inicial e mensalidade. Cada mês registrar gasto efetivo por categoria e saldo.

## Fornecedores e premissas verificáveis

Supabase informa plano Pro a partir de US$25/mês; limites e compute variam por projeto:
https://supabase.com/pricing (consultado em 28/10/2026). Free pode servir ao experimento,
mas verifique suspensão, capacidade, backup e disponibilidade antes de depender dele comercialmente.
O banco local do Compose é PostgreSQL com pgvector; Supabase Auth pode ser usado separadamente.

Vercel Hobby é não comercial: https://vercel.com/docs/plans/hobby. Para vender, incluir
plano comercial vigente ou Next.js na VPS. Não há pressuposto de Vercel gratuito comercial.

Cotação a fazer antes da compra: VPS (RAM para Next/API/worker), backup externo, domínio,
Resend, Asaas, Google APIs e WhatsApp por país/categoria/volume. Não foram atribuídas taxas
não verificadas a esses fornecedores. Não confundir créditos de assinatura de chat com API.

## Custo variável do modelo

Escolher modelo no BE-007. Fórmula por pergunta:

`custo_USD = tokens_entrada / 1e6 × preço_entrada + tokens_saida / 1e6 × preço_saida`

Somar todos os nós e tentativas, embeddings e eventuais ferramentas pagas; converter pelo
câmbio efetivamente pago e incluir tributos. Cenário ilustrativo: 1.000 perguntas ×
(8.000 tokens de entrada + 1.000 de saída) = 8 milhões de entrada e 1 milhão de saída,
antes de retries. Multiplicar pelos preços oficiais do modelo escolhido, não por estimativa
fixa por mensagem. Cache reduz custo apenas quando realmente aplicável.

## Oferta inicial (hipóteses para testar)

Piloto: implantação de R$1.500–3.000 para uma fonte e até três métricas, mais mensalidade
de R$249–499 com cota explícita. Isso é proposta de teste, não preço validado por pesquisa.
Incluir horas de onboarding, suporte e regra adicional; cobrar integrações fora do escopo.
Não ofertar uso ilimitado. Não prometer que uma venda vai acontecer ou pagar a meta de junho.

Exemplo puramente aritmético: 3 clientes × R$349 = R$1.047/mês brutos. Com R$250 de
infra e R$180 de variável total, restariam R$617 antes de impostos, taxas e trabalho.
Trocar as hipóteses pelos custos medidos; margem precisa remunerar suas horas.

## Gates financeiros

- Medir custo por pergunta e por tenant antes de definir a cota do plano.
- Alertar em 70/90% da verba; interromper chamadas pagas ao atingir o teto.
- Se ninguém aceitar conversar após 20 abordagens qualificadas, rever público/mensagem antes de anúncios.
- Se três demos não produzirem piloto, investigar problema/preço/credibilidade antes de construir v2.
- Reavaliar em 30/11 e 31/12/2026 com caixa real, demos, pilotos e horas disponíveis.
