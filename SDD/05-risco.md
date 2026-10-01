# SDD — Classificação de risco

## Origem

PDF §4.3 (Priorização baseada em risco), §5 (Regra de risco).

## Contexto

É o coração do produto e o trecho do PDF com a exigência mais dura:

> "A IA não será responsável por definir o risco. A classificação será feita pelo sistema
> usando regras fixas. Isso deixa o resultado mais fácil de explicar, testar e auditar."

A regra precisa ser simples e explicável. Cada classificação sai acompanhada de uma
justificativa em texto, porque priorizar sem dizer por quê não ajuda ninguém a decidir o
que corrigir primeiro.

## Requisitos funcionais

- RF-1: A prioridade considera **cinco** fatores (§4.3): severidade indicada pela
  ferramenta, confirmação pelo outro scanner, ambiente, exposição e importância para o
  negócio.
- RF-2: A escala tem quatro níveis: Crítico, Alto, Médio e Baixo.
- RF-3: Toda classificação produz uma justificativa em texto legível.
- RF-4: A classificação é determinística: mesma entrada, mesmo resultado.
- RF-5: A severidade original da ferramenta é preservada e exibida ao lado do risco
  calculado, para o usuário comparar as duas leituras.

## Considerações de segurança

- `classificar()` é função **pura**: sem banco, sem rede, sem estado. É o que permite
  auditar e reproduzir.
- `risk_engine.py` não importa `ai_explainer` nem `ai_service`. Não há caminho pelo qual
  uma resposta de modelo altere um nível de risco.

## O que o PDF §5 exige, literalmente

Cada bloco do PDF é uma conjunção — todas as condições listadas precisam valer:

| Nível | Condições, todas juntas |
|---|---|
| **Crítico** | Semgrep e Nuclei confirmam · **o Nuclei encontra evidência relacionada** · aplicação em produção · exposta à internet **ou** de alta importância |
| **Alto** | aplicação em produção · **ainda não há confirmação pelo Nuclei** |
| **Médio/Baixo** | homologação ou teste · baixo impacto · **não existe evidência clara de exploração** |
| **Baixo** | ambiente de teste · baixo impacto · achado apenas teórico |

Duas consequências que a leitura apressada perde:

1. **Evidência é condição do Crítico**, não enfeite. Confirmação dupla sem evidência
   concreta não chega ao topo da escala.
2. **O bloco Médio/Baixo exige "não existe evidência clara de exploração".** Um achado
   confirmado pelas duas ferramentas, com evidência, está **fora** desse bloco por
   definição — mesmo em homologação. O PDF não diz onde ele cai; a matriz abaixo preenche
   a lacuna, e o AC correspondente vai marcado `[extensão]`.

## A matriz

Nível base, antes do ajuste por severidade:

| Confirmação | Ambiente | Contexto de negócio | Evidência | Risco |
|---|---|---|---|---|
| Semgrep **e** Nuclei | Produção | internet **ou** importância alta | sim | **Crítico** |
| Semgrep **e** Nuclei | Produção | internet **ou** importância alta | não | **Alto** |
| Semgrep **e** Nuclei | Produção | interna e importância não-alta | qualquer | **Alto** |
| Semgrep **e** Nuclei | Homologação | qualquer | qualquer | **Alto** |
| Semgrep **e** Nuclei | Teste | qualquer | qualquer | **Médio** |
| uma ferramenta só | Produção | qualquer | qualquer | **Alto** |
| uma ferramenta só | Homologação | qualquer | qualquer | **Médio** |
| uma ferramenta só | Teste | qualquer | qualquer | **Baixo** |

Ajuste pela severidade reportada, no máximo um degrau e mutuamente exclusivo:

- **Desce um nível** quando *todas* as ferramentas que viram o achado o classificaram
  como informativo ou baixo.
- **Sobe um nível** quando alguma ferramenta marcou severidade **crítica** *e* a aplicação
  está em produção *e* é relevante para o negócio. As três condições juntas — do
  contrário todo achado "high" viraria Crítico.

**Invariante acima de tudo: sem evidência não há Crítico.** Vale inclusive para a
elevação por severidade — do contrário a regra do §5 seria contornável por um caminho
lateral.

## O que é "evidência"

Algum achado do grupo traz evidência extraída (`extracted-results`) ou código de status
HTTP. Os dois significam a mesma coisa: o Nuclei alcançou a aplicação de verdade. É o que
separa um achado teórico de um confirmado, e é exatamente o vocabulário que o PDF usa
("evidência relacionada", "evidência clara de exploração", "apenas teórico").

## Critérios de aceitação — testáveis

### A matriz base

- **AC-RISCO-01** — Dado confirmação pelas duas ferramentas **com evidência**, aplicação
  em produção e exposta à internet, quando classificada, então o risco é **Crítico**.

- **AC-RISCO-02** — Dado confirmação pelas duas ferramentas **com evidência**, aplicação
  em produção, interna, com importância alta, quando classificada, então o risco é
  **Crítico** — importância alta substitui a exposição à internet, conforme o PDF §5.

- **AC-RISCO-03** `[extensão]` — Dado confirmação pelas duas ferramentas, aplicação em
  produção, interna e de importância não-alta, quando classificada, então o risco é
  **Alto**.

- **AC-RISCO-04** `[extensão]` — Dado confirmação pelas duas ferramentas e aplicação em
  homologação, quando classificada, então o risco é **Alto**. O PDF exclui este caso do
  bloco Médio/Baixo ao exigir dele "não existe evidência clara de exploração", e não diz
  onde ele cai: a confirmação dupla é justamente a evidência clara. Alto porque o mesmo
  código tende a chegar em produção.

- **AC-RISCO-05** `[extensão]` — Dado confirmação pelas duas ferramentas e aplicação em
  ambiente de teste, quando classificada, então o risco é **Médio**. O PDF reserva Baixo
  para o achado "apenas teórico", que a confirmação dupla desmente.

- **AC-RISCO-06** — Dado achado de uma única ferramenta e aplicação em produção, quando
  classificada, então o risco é **Alto**, conforme as duas condições do PDF §5:
  aplicação em produção e ainda sem confirmação pelo Nuclei.

- **AC-RISCO-07** — Dado achado de uma única ferramenta em produção, quando a aplicação é
  interna e de importância não-alta, então o risco continua **Alto**: o PDF §5 não
  qualifica o Risco Alto por exposição nem por importância, e o contexto de negócio não
  rebaixa o que a especificação já fixou.

- **AC-RISCO-08** — Dado achado de uma única ferramenta e aplicação em homologação, quando
  classificada, então o risco é **Médio**.

- **AC-RISCO-09** — Dado achado de uma única ferramenta e aplicação em ambiente de teste,
  quando classificada, então o risco é **Baixo**.

- **AC-RISCO-22** — Dado confirmação pelas duas ferramentas, aplicação em produção e
  crítica para o negócio, porém **sem evidência** extraída nem status HTTP, quando
  classificada, então o risco é **Alto**, não Crítico: o PDF §5 lista a evidência entre as
  condições do Crítico.

### Ajuste por severidade — o quinto fator

- **AC-RISCO-10** — Dado que todas as ferramentas classificaram o achado como informativo
  ou baixo, quando classificado, então o risco desce exatamente um nível em relação à
  matriz base.

- **AC-RISCO-11** — Dado que alguma ferramenta marcou severidade crítica, a aplicação está
  em produção e é relevante para o negócio, quando classificado, então o risco sobe
  exatamente um nível em relação à matriz base.

- **AC-RISCO-23** — Dado um achado sem evidência que a severidade crítica elevaria até
  Crítico, quando classificado, então o resultado para em **Alto**: a elevação por
  severidade não contorna a exigência de evidência do PDF §5.

- **AC-RISCO-12** — Dado severidade crítica em aplicação que **não** está em produção,
  quando classificada, então **não** há elevação — a condição exige as três juntas.

- **AC-RISCO-13** — Dado um achado já no topo da escala, quando a elevação se aplicaria,
  então o risco permanece Crítico: a escada não passa do topo.

- **AC-RISCO-14** — Dado um achado já no fim da escala, quando o rebaixamento se
  aplicaria, então o risco permanece Baixo: a escada não passa do fundo.

### Explicabilidade e pureza

- **AC-RISCO-15** — Dado qualquer classificação, quando concluída, então vem acompanhada
  de uma justificativa em texto não vazia que cita o ambiente e a situação de confirmação.

- **AC-RISCO-16** — Dado a mesma entrada, quando classificada duas vezes, então o
  resultado é idêntico — nível e justificativa.

- **AC-RISCO-17** `[proibição]` — Dado o módulo `app/services/risk_engine.py`, quando suas
  importações são inspecionadas, então ele **não** importa `ai_explainer`, `ai_service`
  nem qualquer SDK de IA.

- **AC-RISCO-18** `[proibição]` — Dado o módulo `app/services/risk_engine.py`, quando suas
  importações são inspecionadas, então ele **não** importa `sqlalchemy` nem cliente de
  rede: a classificação não depende de banco nem de serviço externo.

- **AC-RISCO-19** — Dado um grupo com achados de severidades diferentes, quando a
  severidade predominante é calculada, então é a mais grave entre elas, e ela **não**
  participa da decisão do nível além do ajuste de um degrau já descrito.

### Contexto de negócio

- **AC-RISCO-20** — Dado uma aplicação exposta à internet **ou** de importância alta,
  quando o contexto é avaliado, então ela é considerada crítica para o negócio; nas demais
  combinações, não.

- **AC-RISCO-21** — Dado vulnerabilidades já classificadas, quando o ambiente, a exposição
  ou a importância da aplicação muda, então todas são reclassificadas com o novo contexto
  e a justificativa é reescrita.

## Casos de borda

- **AC-RISCO-E1** `[extensão]` — Dado um grupo sem nenhum achado, quando classificado,
  então o risco é Baixo com justificativa dizendo que não há evidência para classificar.

- **AC-RISCO-E2** `[extensão]` — Dado um achado cuja severidade a ferramenta não informou,
  quando classificado, então a ausência é tratada como severidade baixa e não quebra a
  classificação.

- **AC-RISCO-E3** — Dado severidades escritas em português ou em inglês (`crítica`,
  `critical`, `alta`, `high`, `error`), quando avaliadas, então são reconhecidas como
  equivalentes.

## Divergências com o PDF — resolvidas

> Três pontos estiveram abertos. Todos fechados relendo o §5 como conjunção de condições,
> que é como ele está escrito. O registro fica para quem vier depois não reabrir a
> discussão do zero.

1. **Produção sem confirmação dinâmica nem contexto crítico** — *alinhado ao PDF.*
   O §5 define Risco Alto por duas condições apenas: "a aplicação está em produção" e
   "ainda não há confirmação pelo Nuclei". Não qualifica por exposição nem por
   importância. A implementação rebaixava para Médio quando a aplicação era interna e de
   importância não-alta, o que acrescentava uma condição que o PDF não pede. **Passou a
   ser Alto em qualquer contexto de produção** (`AC-RISCO-06`, `AC-RISCO-07`). O contexto
   de negócio continua pesando onde o PDF manda: na fronteira entre Alto e Crítico.

2. **Evidência do Nuclei no Crítico** — *alinhado ao PDF.*
   "O Nuclei encontra evidência relacionada" é um dos quatro itens do bloco Crítico, não
   um comentário. **Passou a ser condição necessária** (`AC-RISCO-22`), inclusive contra a
   elevação por severidade (`AC-RISCO-23`) — uma regra contornável por caminho lateral não
   é uma regra.

3. **Homologação e teste com confirmação dupla** — *não era divergência.*
   O bloco Médio/Baixo do PDF exige "não existe evidência clara de exploração", e o bloco
   Baixo exige que "o achado pareça ser apenas teórico". Confirmação pelas duas
   ferramentas é precisamente evidência clara, e desmente o teórico: o caso está **fora**
   dos dois blocos por definição, e o PDF não diz onde ele cai. Alto em homologação
   (`AC-RISCO-04`) e Médio em teste (`AC-RISCO-05`) preenchem a lacuna e seguem marcados
   `[extensão]`, com o raciocínio no próprio AC.

**O que mudou na prática:** um achado só do Semgrep em aplicação de produção interna e de
baixa importância sobe de Médio para Alto; e uma confirmação dupla sem nenhuma evidência
concreta desce de Crítico para Alto.

## Restrições conscientes

- Sem pontuação numérica (CVSS, score 0–10). O PDF pede regra "simples e explicável", e um
  score composto é o oposto de explicável.
- Sem aprendizado com o histórico. Uma vulnerabilidade marcada como falso positivo não
  ensina o motor a rebaixar achados parecidos.

## Validação real

- Fluxo: cadastrar aplicação em produção/internet/alta → enviar os dois relatórios com o
  mesmo XSS → abrir o detalhe da vulnerabilidade → editar a aplicação para ambiente Teste
  → reabrir o detalhe.
- O que deve aparecer: Crítico antes, Médio depois, com a justificativa reescrita citando
  o ambiente de teste.
- Critério: o nível muda e o texto da justificativa muda junto — nunca um sem o outro.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
