# SDD — Interface

## Origem

PDF §7 (Interface e Tecnologias — as quatro telas e seus campos), §13 Etapa 5.

## Contexto

O PDF enumera quatro telas e, para cada uma, exatamente o que precisa aparecer. Esta SDD
transforma cada item daquelas listas em um AC verificável, porque "a tela mostra o
suficiente" não é critério — "a tela mostra a severidade original" é.

A comunicação com o backend é por API REST; o React não fala com o banco.

## Requisitos funcionais

**Tela inicial — Visão geral (§7):** total de aplicações, total de vulnerabilidades,
vulnerabilidades críticas, vulnerabilidades em correção, aplicações com maior risco.

**Tela de aplicações (§7):** lista de aplicações, ambiente, exposição, importância para o
negócio, quantidade de vulnerabilidades.

**Tela de vulnerabilidades (§7):** nome da vulnerabilidade, aplicação afetada, origem
(Semgrep ou Nuclei), severidade, risco calculado pelo PRIDE, status da correção, data da
identificação.

**Tela de detalhes (§7):** explicação da vulnerabilidade, arquivo e linha quando
disponíveis, endpoint ou URL afetada, evidência do Nuclei, justificativa da classificação,
sugestão da IA, botão para alterar o status.

**Login (§10):** login simples.

## Considerações de segurança

- O token fica em `localStorage` e é enviado pelo interceptor do Axios.
- Resposta 401 derruba a sessão em qualquer tela, via evento — não caso a caso.
- Nenhuma tela renderiza HTML vindo da API sem escape. Mensagem de ferramenta e resposta
  de IA são texto.

## Critérios de aceitação — testáveis

### Tela inicial — Visão geral

- **AC-UI-01** — Dado dados de dashboard carregados, quando a visão geral é exibida, então
  mostra o total de aplicações.
- **AC-UI-02** — Dado dados de dashboard carregados, quando a visão geral é exibida, então
  mostra o total de vulnerabilidades.
- **AC-UI-03** — Dado dados de dashboard carregados, quando a visão geral é exibida, então
  mostra a quantidade de vulnerabilidades críticas.
- **AC-UI-04** — Dado dados de dashboard carregados, quando a visão geral é exibida, então
  mostra a quantidade de vulnerabilidades em correção.
- **AC-UI-05** — Dado aplicações com vulnerabilidades, quando a visão geral é exibida,
  então mostra a lista de aplicações com maior risco, com ambiente e exposição de cada uma.
- **AC-UI-06** `[extensão]` — Dado nenhuma aplicação cadastrada, quando a visão geral é
  exibida, então aparece um estado vazio orientando a cadastrar uma aplicação, e não uma
  tela de zeros.

### Tela de aplicações

- **AC-UI-07** — Dado aplicações cadastradas, quando a tela de aplicações é exibida, então
  lista cada aplicação com nome, ambiente, exposição e importância para o negócio.
- **AC-UI-08** — Dado aplicações com vulnerabilidades, quando a tela de aplicações é
  exibida, então mostra a quantidade de vulnerabilidades de cada uma.
- **AC-UI-09** — Dado o formulário de cadastro, quando exibido, então oferece os campos
  nome, responsável, ambiente, exposição, importância e URL.
- **AC-UI-10** — Dado o formulário preenchido, quando enviado, então a aplicação é
  cadastrada e passa a aparecer na lista.
- **AC-UI-11** `[extensão]` — Dado uma aplicação cadastrada, quando o envio de relatório é
  acionado a partir dela, então é possível enviar o arquivo do Semgrep e o do Nuclei.

### Tela de vulnerabilidades

- **AC-UI-12** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra o nome/tipo da vulnerabilidade.
- **AC-UI-13** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra a aplicação afetada.
- **AC-UI-14** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra a origem: Semgrep, Nuclei ou ambas.
- **AC-UI-15** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra a severidade original informada pela ferramenta.
- **AC-UI-16** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra o risco calculado pelo PRIDE.
- **AC-UI-17** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra o status da correção.
- **AC-UI-18** — Dado vulnerabilidades carregadas, quando a lista é exibida, então cada
  linha mostra a data da identificação.
- **AC-UI-19** `[extensão]` — Dado a lista exibida, quando os filtros são usados, então é
  possível filtrar por aplicação, risco, status e somente correlacionadas, e o filtro
  aplicado fica na URL.
- **AC-UI-20** `[extensão]` — Dado nenhuma vulnerabilidade correspondente, quando a lista é
  exibida, então aparece um estado vazio explicando o que fazer.

### Tela de detalhes

- **AC-UI-21** — Dado uma vulnerabilidade, quando o detalhe é exibido, então mostra a
  justificativa da classificação.
- **AC-UI-22** — Dado um achado do Semgrep com arquivo e linha, quando o detalhe é exibido,
  então mostra arquivo e linha.
- **AC-UI-23** — Dado uma vulnerabilidade, quando o detalhe é exibido, então mostra o
  endpoint afetado e, havendo achado do Nuclei, a URL.
- **AC-UI-24** — Dado um achado do Nuclei com evidência, quando o detalhe é exibido, então
  mostra a evidência.
- **AC-UI-25** — Dado uma análise de IA já gerada, quando o detalhe é exibido, então mostra
  a explicação, o impacto, a justificativa da priorização, a sugestão de correção, como
  validar e a descrição para ticket.
- **AC-UI-26** — Dado uma vulnerabilidade, quando o detalhe é exibido, então oferece
  controle para alterar o status entre os cinco valores.
- **AC-UI-27** — Dado o controle de status, quando um novo status é escolhido, então a
  mudança é enviada à API e a tela reflete o novo status.
- **AC-UI-28** `[extensão]` — Dado uma vulnerabilidade com histórico, quando o detalhe é
  exibido, então mostra o histórico com autor e data de cada mudança.
- **AC-UI-29** `[extensão]` — Dado que ainda não há análise de IA, quando o detalhe é
  exibido, então explica que a IA recebe o risco já classificado e não participa da
  decisão, com um botão para gerar a explicação.

### Login

- **AC-UI-30** — Dado a tela de login, quando exibida, então oferece campos de e-mail e
  senha e um botão de entrar.
- **AC-UI-31** — Dado credenciais válidas, quando o login é enviado, então o token é
  guardado e o usuário chega à visão geral.
- **AC-UI-32** — Dado credenciais inválidas, quando o login é enviado, então a mensagem de
  erro da API é exibida e o usuário permanece na tela de login.

### Contrato de dados da visão geral

> A tela do §7 só mostra o que a API entrega. Estes ACs são a metade de backend dos
> `AC-UI-01` a `AC-UI-05`, provada sem navegador.

- **AC-UI-33** — Dado aplicações e vulnerabilidades cadastradas, quando o dashboard é
  consultado, então a API devolve total de aplicações, total de vulnerabilidades, total de
  críticas, total em correção e total corrigidas.

- **AC-UI-34** — Dado vulnerabilidades de riscos variados, quando o dashboard é consultado,
  então a contagem por risco cobre os quatro níveis, na ordem Crítico → Alto → Médio →
  Baixo.

- **AC-UI-35** — Dado aplicações com vulnerabilidades, quando o dashboard é consultado,
  então o ranking de aplicações em risco traz nome, ambiente, exposição, quantidade de
  críticas, de altas, o total e a pontuação que ordena a lista.

## Casos de borda

- **AC-UI-E1** — Dado que a API está fora do ar, quando uma tela carrega, então aparece
  mensagem dizendo que não foi possível falar com o servidor, com opção de tentar de novo.
- **AC-UI-E2** — Dado que a API respondeu 401, quando qualquer tela faz uma chamada, então
  a sessão é encerrada e o usuário volta ao login.
- **AC-UI-E3** — Dado que os dados ainda estão carregando, quando a tela é exibida, então
  aparece o indicador de carregamento, não uma tela em branco.
- **AC-UI-E4** `[extensão]` — Dado uma vulnerabilidade sem severidade original, quando a
  lista é exibida, então a célula mostra um traço, não vazio nem "null".

- **AC-UI-E5** — Dado uma base sem nenhuma aplicação, quando o dashboard é consultado,
  então todos os totais vêm zerados e o ranking vem como lista vazia, sem erro.

## Restrições conscientes

- Sem paginação. A lista traz tudo. Um inventário grande exigiria AC novo.
- Sem tema escuro, sem internacionalização. A interface é em português.
- Sem edição de aplicação a partir da tela de vulnerabilidades — só pela tela de
  aplicações.

## Validação real

- Fluxo: percorrer as quatro telas com dados de `popular_demo.py`.
- O que deve aparecer: cada item das listas do §7 do PDF, visível sem rolar até o rodapé.
- Critério: nenhum campo exigido pelo PDF ausente, e nenhum "undefined" na tela.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
