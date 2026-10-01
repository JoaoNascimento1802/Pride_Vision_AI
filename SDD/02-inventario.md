# SDD — Inventário de aplicações

## Origem

PDF §4.1 (Inventário de aplicações) — o primeiro dos quatro pilares de ASPM.

## Contexto

O inventário é onde entram os dados de contexto que o motor de risco usa depois para
priorizar. Sem ambiente, exposição e importância, a plataforma seria um comparador de
arquivos: a mesma falha valeria o mesmo num sandbox interno e num portal público.

O PDF dá o exemplo exato do que precisa caber:

```
Aplicação: Portal do Cliente
Ambiente: Produção
Exposição: Internet
Importância: Alta
```

## Requisitos funcionais

- RF-1: Cadastrar aplicação com nome, responsável, ambiente, URL, exposição e importância
  para o negócio.
- RF-2: Ambiente é um entre Produção, Homologação e Teste.
- RF-3: Exposição é um entre Internet e Interna.
- RF-4: Importância é um entre Alta, Média e Baixa.
- RF-5: A lista de aplicações mostra ambiente, exposição, importância e a quantidade de
  vulnerabilidades de cada uma (PDF §7, tela de aplicações).

## Considerações de segurança

- Todas as rotas de `/api/aplicacoes` exigem usuário autenticado.
- A URL é armazenada como texto de inventário. Não é resolvida, não é acessada.
- Não há isolamento por empresa: qualquer usuário autenticado vê e edita todo o
  inventário. É a leitura literal de "login simples" no MVP — ver `09-arquitetura.md`.

## Critérios de aceitação — testáveis

- **AC-INV-01** — Dado um usuário autenticado, quando cadastra uma aplicação com nome,
  responsável, ambiente, exposição, importância e URL, então a API responde 201 e devolve
  os seis campos gravados.

- **AC-INV-02** — Dado o vocabulário de ambiente, quando uma aplicação é cadastrada com
  `producao`, `homologacao` ou `teste`, então o cadastro é aceito.

- **AC-INV-03** — Dado o vocabulário de exposição, quando uma aplicação é cadastrada com
  `internet` ou `interna`, então o cadastro é aceito.

- **AC-INV-04** — Dado o vocabulário de importância, quando uma aplicação é cadastrada com
  `alta`, `media` ou `baixa`, então o cadastro é aceito.

- **AC-INV-05** — Dado um valor fora do vocabulário controlado em ambiente, exposição ou
  importância, quando o cadastro é tentado, então a API responde 422 e nada é gravado.

- **AC-INV-06** — Dado aplicações cadastradas com vulnerabilidades, quando a lista é
  consultada, então cada item traz ambiente, exposição, importância e a quantidade total
  de vulnerabilidades.

- **AC-INV-07** — Dado que a URL é opcional, quando uma aplicação é cadastrada sem URL,
  então o cadastro é aceito e a URL fica nula.

- **AC-INV-08** — Dado uma aplicação com vulnerabilidades já classificadas, quando seu
  ambiente, exposição ou importância é alterado, então as vulnerabilidades são
  reclassificadas na hora com o novo contexto.

- **AC-INV-09** `[extensão]` — Dado uma aplicação com uploads, achados e vulnerabilidades,
  quando ela é removida, então tudo que veio dela é removido em cascata.

- **AC-INV-10** `[proibição]` — Dado uma requisição sem token, quando qualquer rota de
  `/api/aplicacoes` é chamada, então a API responde 401 e nenhum dado de inventário é
  devolvido.

- **AC-INV-11** — Dado uma aplicação cadastrada, quando o resumo dela é consultado, então
  vêm as contagens por risco e por status daquela aplicação.

## Casos de borda

- **AC-INV-E1** — Dado um nome com menos de 2 caracteres, quando o cadastro é tentado,
  então a API responde 422.

- **AC-INV-E2** — Dado um identificador de aplicação inexistente, quando ela é consultada,
  editada ou removida, então a API responde 404 com mensagem em português.

- **AC-INV-E3** `[extensão]` — Dado nome e responsável com espaços nas pontas, quando a
  aplicação é cadastrada, então os valores são gravados sem os espaços.

- **AC-INV-E4** — Dado uma aplicação sem nenhuma vulnerabilidade, quando a lista é
  consultada, então os contadores vêm zerados, não ausentes.

## Contrato de API

| Método | Rota | Corpo | Resposta | Erros |
|---|---|---|---|---|
| GET | `/api/aplicacoes` | — | `ApplicationListItem[]` | 401 |
| POST | `/api/aplicacoes` | `ApplicationCreate` | 201 `ApplicationResponse` | 401, 422 |
| GET | `/api/aplicacoes/{id}` | — | `ApplicationResponse` | 401, 404 |
| PATCH | `/api/aplicacoes/{id}` | `ApplicationUpdate` (parcial) | `ApplicationResponse` | 401, 404, 422 |
| DELETE | `/api/aplicacoes/{id}` | — | 204 | 401, 404 |
| GET | `/api/aplicacoes/{id}/resumo` | — | contagens por risco e status | 401, 404 |

## Restrições conscientes

- Sem papéis nem permissões por aplicação. Qualquer usuário autenticado pode editar e
  remover qualquer aplicação.
- Sem histórico de alteração do cadastro. O histórico existe para o status da
  vulnerabilidade (`07-acompanhamento.md`), não para o inventário.

## Validação real

- Fluxo: cadastrar "Portal do Cliente" (produção / internet / alta) → conferir na lista →
  editar para ambiente Teste → reabrir a lista de vulnerabilidades.
- O que deve aparecer: as vulnerabilidades antes Críticas descem de nível ao virar Teste.
- Critério: a justificativa exibida passa a citar "ambiente de teste".

## Status

- [x] Spec aprovada pelo usuário
- [x] Testes escritos — vermelhos
- [x] Implementação concluída — testes verdes
- [x] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
