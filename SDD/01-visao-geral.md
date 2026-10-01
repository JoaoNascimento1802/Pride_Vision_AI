# SDD — Visão geral e fluxo ponta a ponta

## Origem

PDF §1 (Ideia do projeto), §2 (Problema), §3 (Como o sistema funcionará), §14 (Definição
final).

## Contexto

Ferramentas de segurança geram muitos alertas e nem todos importam igualmente. O Semgrep
lê o código e aponta trechos suspeitos; o Nuclei ataca a aplicação rodando e confirma o
que responde. O PRIDE cruza as duas visões e acrescenta o contexto de negócio para
responder a uma pergunta: **qual vulnerabilidade precisa ser corrigida primeiro?**

O objetivo declarado no PDF não é criar outro scanner. É uma central de organização,
priorização e acompanhamento — a ideia principal de uma solução ASPM.

## Requisitos funcionais

- RF-1: O fluxo é `cadastro da aplicação → upload Semgrep → upload Nuclei → organização →
  correlação → classificação de risco → explicação por IA → acompanhamento da correção`.
- RF-2: A primeira versão recebe os arquivos **manualmente**.
- RF-3: O sistema **não** executa o Semgrep nem o Nuclei.
- RF-4: A lista de vulnerabilidades responde à pergunta da priorização — a mais grave
  aparece primeiro.

## Considerações de segurança

- Toda rota que devolve dado de vulnerabilidade exige autenticação.
- A URL cadastrada de uma aplicação é **dado de inventário**, nunca alvo: nenhum código
  do produto faz requisição para ela.

## Critérios de aceitação — testáveis

- **AC-FLUXO-01** — Dado uma aplicação cadastrada, quando o relatório do Semgrep é
  enviado e em seguida o do Nuclei, então a lista de vulnerabilidades traz o problema
  comum às duas ferramentas com risco calculado e justificativa preenchida.

- **AC-FLUXO-02** — Dado vulnerabilidades de riscos diferentes na mesma base, quando a
  lista é consultada, então elas vêm ordenadas de Crítico para Baixo.

- **AC-FLUXO-03** `[proibição]` — Dado os módulos de ingestão, correlação e risco, quando
  suas dependências são inspecionadas, então nenhum importa cliente HTTP
  (`requests`, `httpx`, `urllib.request`, `socket`): a plataforma não alcança o alvo e,
  portanto, não varre nada.

- **AC-FLUXO-04** `[proibição]` — Dado o conjunto de rotas publicadas pela API, quando
  inspecionado, então não existe rota que dispare varredura, execução de ferramenta ou
  chamada ao alvo — as únicas entradas de achado são os dois uploads.

- **AC-FLUXO-05** `[extensão]` — Dado uma base sem nenhum relatório enviado, quando a
  lista de vulnerabilidades é consultada, então a resposta é uma lista vazia com HTTP
  200, não um erro.

- **AC-FLUXO-06** — Dado que o mesmo problema foi apontado pelas duas ferramentas, quando
  a vulnerabilidade é consultada, então ela indica que foi encontrada pelo Semgrep **e**
  confirmada pelo Nuclei.

- **AC-FLUXO-07** `[proibição]` — Dado uma requisição sem token, quando qualquer rota que
  devolve dado de vulnerabilidade é chamada (listagem, detalhe, dashboard), então a API
  responde 401 e nenhum dado é devolvido.

## Casos de borda

- **AC-FLUXO-E1** — Dado que só o relatório do Semgrep foi enviado, quando a lista é
  consultada, então as vulnerabilidades aparecem marcadas como não confirmadas
  dinamicamente, e não são descartadas.

- **AC-FLUXO-E2** — Dado que o relatório do Nuclei chega **depois** do Semgrep, quando a
  ingestão termina, então a correlação considera os achados antigos já gravados e não só
  os do upload atual.

- **AC-FLUXO-E3** — Dado um identificador de vulnerabilidade inexistente, quando o detalhe
  é consultado, então a API responde 404 com mensagem em português.

## Restrições conscientes

- Ingestão manual. Integração com CI, webhook ou execução agendada está fora do MVP
  (PDF §3: "A primeira versão receberá os arquivos manualmente").
- Sem multi-empresa. Todo usuário autenticado enxerga todo o inventário — ver
  `09-arquitetura.md`.

## Validação real

- Fluxo: login → cadastrar "Portal do Cliente" (produção / internet / alta) → enviar
  `semgrep.json` → enviar `nuclei.jsonl` → abrir a lista de vulnerabilidades.
- O que deve aparecer: pelo menos uma vulnerabilidade Crítica no topo, com as duas
  ferramentas indicadas e justificativa citando produção e exposição.
- Critério: a ordem da lista é decrescente por risco e a justificativa não está vazia.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
