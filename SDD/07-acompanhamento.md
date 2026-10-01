# SDD — Acompanhamento da correção

## Origem

PDF §4.4 (Acompanhamento da correção), §7 (botão para alterar o status), §10 (alteração do
status de correção), §13 Etapa 7.

## Contexto

> "Essa parte é importante para o conceito de ASPM, pois a plataforma não apenas mostra
> vulnerabilidades: ela também ajuda a acompanhar o ciclo de tratamento."

É o que separa uma plataforma de ASPM de um relatório. Sem o ciclo de status, não há como
responder quando algo foi corrigido nem por quem.

## Requisitos funcionais

- RF-1: Cada vulnerabilidade tem um status entre: **Nova**, **Em análise**,
  **Em correção**, **Corrigida** e **Falso positivo**.
- RF-2: O usuário pode alterar o status.
- RF-3: A plataforma exibe a quantidade de vulnerabilidades por status.
- RF-4: O status é preservado quando um novo relatório é enviado.

## Considerações de segurança

- Alterar status exige usuário autenticado, e o autor da mudança é registrado.
- O status é escrito **apenas** por ação humana. Nem a ingestão nem a IA o alteram.

## Critérios de aceitação — testáveis

- **AC-STATUS-01** — Dado o vocabulário de status, quando consultado, então existem
  exatamente cinco: Nova, Em análise, Em correção, Corrigida e Falso positivo.

- **AC-STATUS-02** — Dado uma vulnerabilidade recém-identificada na ingestão, quando
  consultada, então seu status é **Nova**.

- **AC-STATUS-03** — Dado uma vulnerabilidade com status Nova, quando o usuário a marca
  como Em correção, então o novo status é gravado e devolvido.

- **AC-STATUS-04** — Dado uma vulnerabilidade, quando o usuário a marca como Corrigida,
  então o novo status é gravado e ela deixa de contar como aberta.

- **AC-STATUS-05** — Dado uma vulnerabilidade, quando o usuário a marca como Falso
  positivo, então o novo status é gravado e ela deixa de contar como aberta.

- **AC-STATUS-06** `[extensão]` — Dado uma mudança de status, quando gravada, então o
  histórico registra status anterior, status novo, o usuário que mudou, o instante e o
  comentário opcional.

- **AC-STATUS-07** — Dado uma vulnerabilidade com histórico, quando o detalhe é
  consultado, então o histórico completo vem junto, com o nome de quem fez cada mudança.

- **AC-STATUS-08** — Dado vulnerabilidades em status diferentes, quando o dashboard é
  consultado, então traz a contagem por status.

- **AC-STATUS-09** — Dado uma vulnerabilidade cujo status o usuário já mudou para Em
  correção, quando um novo relatório é enviado e a vulnerabilidade continua existindo,
  então o status **Em correção** é preservado — não volta para Nova.

- **AC-STATUS-10** `[proibição]` — Dado uma ingestão de relatório, quando concluída, então
  nenhum status de vulnerabilidade existente é alterado pela ingestão.

- **AC-STATUS-11** — Dado uma vulnerabilidade, quando a lista é filtrada por um status,
  então só as vulnerabilidades naquele status são devolvidas.

- **AC-STATUS-12** `[extensão]` — Dado os status Corrigida e Falso positivo, quando
  avaliados, então são considerados encerrados; Nova, Em análise e Em correção são
  considerados abertos.

## Casos de borda

- **AC-STATUS-E1** `[extensão]` — Dado uma vulnerabilidade já no status desejado, quando o
  usuário tenta mudá-la para o mesmo status, então a API responde 409 e nenhum registro
  duplicado entra no histórico.

- **AC-STATUS-E2** — Dado um status fora do vocabulário, quando a mudança é tentada, então
  a API responde 422.

- **AC-STATUS-E3** — Dado uma vulnerabilidade inexistente, quando a mudança de status é
  tentada, então a API responde 404.

- **AC-STATUS-E4** — Dado uma mudança de status sem comentário, quando gravada, então é
  aceita e o comentário fica nulo.

- **AC-STATUS-E5** — Dado uma requisição sem token, quando a mudança de status é tentada,
  então a API responde 401 e nada é alterado.

## Contrato de API

| Método | Rota | Corpo | Resposta | Erros |
|---|---|---|---|---|
| PATCH | `/api/vulnerabilidades/{id}/status` | `{status, comentario?}` | `VulnerabilidadeDetalhe` | 401, 404, 409, 422 |

## Restrições conscientes

- **Não há máquina de estados.** Qualquer status pode ir para qualquer outro (exceto para
  ele mesmo). Proibir "Corrigida → Nova" pareceria mais rigoroso, mas na prática impediria
  reabrir uma correção que não funcionou.
- **Sem prazo, sem responsável por vulnerabilidade, sem SLA.** O responsável existe no
  inventário, por aplicação. Vulnerabilidade não tem dono próprio no MVP.
- **Vulnerabilidade que some do relatório é removida, e o histórico dela vai junto.** É
  consequência de a plataforma refletir a varredura mais recente. Quem precisar de
  auditoria de longo prazo precisa de um AC novo.

## Validação real

- Fluxo: abrir uma vulnerabilidade → mudar para "Em correção" com um comentário → voltar
  ao dashboard → reenviar o mesmo `semgrep.json` → reabrir a vulnerabilidade.
- O que deve aparecer: o contador "em correção" incrementado no dashboard; após o reenvio,
  o status continua "Em correção" e o histórico mostra a mudança com o autor.
- Critério: o status sobrevive ao reenvio do relatório.

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
