---
description: Katrina audita o sistema contra o PDF original e aponta divergência, ausência e escopo extra
---

Delegue ao agent **katrina-bennett**: auditar o sistema contra a especificação original.

Escopo da auditoria: $ARGUMENTS (sem argumento, audite o PDF inteiro, seção por seção)

## As fontes

1. `SDD/anexos/PRIDE-Vision-AI.pdf` — o contrato original
2. `SDD/anexos/spec-extraida.txt` — o mesmo texto, pesquisável (use este para citar)
3. `SDD/*.md` — o contrato decomposto em ACs

Quando SDD e PDF divergem, **o PDF vence** e a divergência é achado.

## O que procurar

1. **Critério do PDF sem AC** — frase que impõe comportamento e não virou AC.
2. **AC sem teste** — rode `python scripts/rastreabilidade.py`. Conformidade não provada
   não é conformidade.
3. **Comportamento diferente do texto** — o mais importante. Cite o trecho do PDF, cite o
   código, mostre a diferença e **não decida**: a decisão é do usuário.
4. **Escopo extra** — o §10 diz "somente". O que existe fora daqueles onze itens é achado.
5. **Marca `[extensão]` errada** — faltando (esconde decisão de projeto) ou sobrando
   (esconde conformidade real).

## Regras

- **Read-only.** Não corrija, não edite a SDD, não escreva teste. Seu produto é o
  relatório.
- Cite sempre: seção do PDF, ID do AC, arquivo e linha do código.
- Não invente achado para parecer útil. Seção conforme se declara conforme.
- Divergências já conhecidas estão registradas em `SDD/05-risco.md`, seção "Divergências
  com o PDF". Confirme se continuam valendo; não as reapresente como novidade.
