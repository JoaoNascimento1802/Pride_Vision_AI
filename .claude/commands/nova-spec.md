---
description: Entrevista de requisitos e redação da SDD com ACs numerados, antes de qualquer código
---

Conduza a entrevista de requisitos e escreva a SDD seguindo
`SDD/templates/SPEC_TEMPLATE.md`. Delegue ao agent **harvey**.

Assunto a especificar: $ARGUMENTS

## Passos obrigatórios

1. **Harvey entrevista o usuário** — perguntas objetivas, uma rodada por vez:
   - O que exatamente isso deve entregar? Qual o resultado observável?
   - O que **não** pode acontecer?
   - Casos de borda: entrada vazia, inválida, no limite; aplicação sem vulnerabilidade;
     relatório malformado; provedor de IA fora do ar
   - Tem endpoint? Tem tela? Mexe em model (lembre: **não há migrações**)?
   - Encosta nas regras 3 a 6 do `AGENTS.md`?

2. **Confronte com o PDF** (`SDD/anexos/spec-extraida.txt`). Diga ao usuário, para cada
   ponto, se consta no PDF, se é extensão, ou se está fora do §10 do MVP.

3. **Escreva a SDD** no documento certo de `SDD/` — veja `SDD/00-INDICE.md` para o prefixo
   de ID. Cada AC no formato Dado/Quando/Então. Marque `[extensão]` e `[proibição]` onde
   couber.

4. **Apresente e AGUARDE aprovação explícita.** Sem aprovação: nada de teste, nada de
   código.

5. **Após aprovação**, delegue a **robert-zane** para derivar os testes dos ACs — eles
   nascem vermelhos, antes de qualquer implementação.

6. **Só então** Harvey delega a implementação a **louis-litt** (backend) ou **mike-ross**
   (frontend).

## Regras

- Nunca pule a entrevista, mesmo que o pedido pareça óbvio.
- Spec não aprovada = nada de teste, nada de código.
- Fix pequeno: formato reduzido com AC único, mas sempre acordado antes.
- Ao terminar de gravar a SDD, rode `python scripts/rastreabilidade.py` — os ACs novos
  vão aparecer como órfãos, e é exatamente essa a lista de trabalho do Robert.
