# SDD — CI/CD Security Gates

## Origem

Especificação §4 (pilares ASPM), §10 (escopo MVP — item 8: acompanhamento da
correção com gate de qualidade) e demanda explícita do usuário para integração
com fluxos de CI/CD.

## Contexto

O PRIDE deve participar ativamente do fluxo de CI/CD, avaliando as políticas de
segurança antes de um deploy ou merge. A decisão é sempre determinística e
calculada localmente — o pipeline não pode impor um resultado.

## Critérios de aceitação

### Política de segurança

- **AC-CI-01** — Dado que o usuário com permissão `policy:write` envia uma política
  válida em `POST /api/ci/policies`, quando a requisição é processada, então a
  política é criada no banco com `ativa=True` e retornada com status 201.

- **AC-CI-02** — Dado que o usuário com permissão `policy:read` acessa
  `GET /api/ci/policies`, então a resposta lista apenas as políticas ativas.

- **AC-CI-03** — Dado que o usuário com permissão `policy:write` envia
  `DELETE /api/ci/policies/{id}`, então a política é desativada (soft delete,
  `ativa=False`) e o endpoint retorna 204 sem remover o registro.

- **AC-CI-04** — Dado que um usuário com papel `DEVELOPER` tenta criar uma política
  via `POST /api/ci/policies`, então a requisição é rejeitada com 403.

### Security Gate

- **AC-CI-05** — Dado que um pipeline com permissão `gate:check` envia um payload
  válido para `POST /api/ci/check`, quando a aplicação não possui vulnerabilidades
  abertas nem políticas ativas, então a decisão retornada é `"pass"`.

- **AC-CI-06** — Dado que a aplicação possui uma vulnerabilidade com risco `CRITICO`
  e existe uma política global com `risco_minimo=critico` e `acao=block`, quando o
  pipeline chama `POST /api/ci/check`, então a decisão retornada é `"block"`.

- **AC-CI-07** — Dado o cenário do AC-CI-06, quando existe uma `PolicyException`
  válida (não expirada) para aquela vulnerabilidade e política, então a decisão
  muda para `"pass"` (a exceção cobre a violação).

- **AC-CI-08** — Dado que a exceção do AC-CI-07 está expirada (data passada), então
  a decisão retorna a ser `"block"`.

- **AC-CI-09** — Dado que existe uma política com `acao=warn` e a vulnerabilidade
  atinge o risco mínimo sem exceção, então a decisão é `"warn"`.

- **AC-CI-10** — Dado que existem duas políticas: uma com `acao=block` e outra com
  `acao=warn`, e a vulnerabilidade viola ambas, então a decisão final é `"block"`
  (a mais restritiva prevalece).

### Idempotência

- **AC-CI-11** — Dado que o mesmo pipeline chama `POST /api/ci/check` duas vezes com
  idênticos `pipeline_id` e `commit_sha`, então apenas um `PipelineRun` é criado,
  mas dois `SecurityGateResult` são registrados (histórico imutável).

- **AC-CI-12** — Dado que o `pipeline_id` e o `commit_sha` são `null`, então cada
  chamada a `POST /api/ci/check` cria um novo `PipelineRun`.

### Exceções de política

- **AC-CI-13** — Dado que o usuário com permissão `exception:write` cria uma
  `PolicyException` via `POST /api/ci/exceptions`, então a exceção é persistida e
  retornada com `valida=True` enquanto a data de expiração não tiver passado.

- **AC-CI-14** — Dado que a exceção possui `expira_em=None`, então `valida` é sempre
  `True` (exceção permanente).

- **AC-CI-15** — Dado que um usuário com papel `DEVELOPER` tenta criar uma exceção,
  então a requisição é rejeitada com 403.

### Histórico

- **AC-CI-16** — Dado que existem `SecurityGateResult` registrados, quando o usuário
  acessa `GET /api/ci/gate-results?aplicacao_id={id}`, então a resposta lista os
  resultados em ordem decrescente de `avaliado_em`.

- **AC-CI-17** — Dado que existem `PipelineRun` registrados, quando o usuário acessa
  `GET /api/ci/pipelines?aplicacao_id={id}`, então a resposta inclui o campo
  `ultimo_resultado` com os dados do `SecurityGateResult` mais recente.

### Segurança

- **AC-CI-18** — Dado que qualquer usuário envia `{"decision": "pass"}` no payload de
  `POST /api/ci/check`, então esse campo é ignorado — a decisão é sempre calculada
  pelo PRIDE internamente.

- **AC-CI-19** — Dado que um usuário sem autenticação chama `POST /api/ci/check`,
  então a resposta é 401.

- **AC-CI-20** — Dado que a resposta do Security Gate é retornada, então ela não
  contém tokens, senhas, chaves de API ou segredos internos.
