# SDD — <nome do módulo ou da feature>

> Preenchida por Harvey a partir da entrevista de requisitos com o usuário.
> Nenhum teste e nenhum código é escrito antes desta spec estar **APROVADA**.
> Regra-fonte: `AGENTS.md` #1 e #2.

## Origem

<qual seção do PDF em `SDD/anexos/` esta spec traduz, ou "novo — não consta no PDF">

## Contexto

<por que isto existe — 2 a 4 frases>

## Requisitos funcionais

- RF-1: ...
- RF-2: ...

## Requisitos não-funcionais (se houver)

- RNF-1: <desempenho, acessibilidade, responsividade, i18n...>

## Considerações de segurança

- Quem pode chamar? (rota autenticada? qualquer usuário logado?)
- Entra dado de fora? Como é validado?
- Algum texto pode chegar a um provedor de IA? Passa por `mascarar()`?
- Alguma coisa aqui poderia decidir risco? (Se sim, **pare** — regra 3.)

## Critérios de aceitação — testáveis

> Cada AC vira ≥1 teste **antes** da implementação. O teste cita o ID.
> ID no formato `AC-<PREFIXO>-<nn>`. O prefixo é o do módulo (ver `SDD/00-INDICE.md`).

- **AC-XXX-01** — Dado <estado inicial>, quando <ação>, então <resultado observável>.
- **AC-XXX-02** — ...

Marque com `[extensão]` o AC que **não** vem do PDF: é decisão de projeto preenchendo
lacuna da especificação. O usuário precisa saber distinguir um do outro.

## Casos de borda

- **AC-XXX-E1** — Dado <entrada inválida, vazia ou no limite>, então <comportamento esperado>.

## Contrato de API (se aplicável)

> Pré-requisito para Robert escrever teste de endpoint. Não deixe em branco se há rota.

| Método | Rota | Corpo | Resposta | Erros |
|---|---|---|---|---|
| | | | | |

## Restrições conscientes

> O que **não** vai ser feito, e por quê. Isto não é desvio — é decisão registrada.

- ...

## Validação real

> "Os testes passaram" não basta. Descreva o que executar na aplicação de pé.

- Fluxo:
- O que deve aparecer na tela / no payload:
- Critério: <condição objetiva>

## Status

- [ ] Spec aprovada pelo usuário (sem AC em branco; contrato de API preenchido se aplicável)
- [ ] Testes escritos (Robert Zane) — vermelhos
- [ ] Implementação concluída — testes verdes
- [ ] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada
