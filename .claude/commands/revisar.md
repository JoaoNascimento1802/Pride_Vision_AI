---
description: Revisão dual obrigatória — Robert (QA) e Jessica (segurança) em paralelo
---

Revisão dual antes de dar qualquer mudança por concluída. Dispare os dois agents **em
paralelo**, não em sequência: eles olham coisas diferentes e um não depende do outro.

Alvo da revisão: $ARGUMENTS (sem argumento, revise as mudanças da sessão atual)

## Em paralelo

**robert-zane** — QA:
- Cada AC tocado tem teste que o cita
- Testes novos cobrindo o comportamento alterado, não só os existentes passando
- Caminho feliz, erro (401/403/404/409/422), borda (nulo, vazio, limite)
- Dependentes rastreados; regressão conferida
- `py_compile`, `ruff`, `mypy --strict`, `vitest`, `build`
- `python scripts/rastreabilidade.py` verde

**jessica-pearson** — segurança:
- As quatro regras do PRIDE: IA não decide risco, masking antes de qualquer envio, IA não
  age, sem varredura no alvo
- OWASP Top 10 no contexto deste produto
- Superfícies próprias: upload, prompt da IA, dados de demonstração

## Critério de merge

| Critério | Regra |
|---|---|
| Robert | APROVADO, com teste novo cobrindo o que mudou |
| Jessica | APROVADO, sem achado crítico ou alto |
| Gate | `scripts/verificar.ps1` verde nas seis etapas |

Qualquer um falhando: **BLOQUEADO**. Reporte ao usuário e pare. Não prossiga "porque é
pequeno".

## Achado durante a revisão

Preferência é corrigir na mesma passada — Robert escreve o teste, quem implementou
corrige. Só adie se o usuário, consultado, decidir adiar conscientemente. Registrar
pendência não é o primeiro destino de um achado; é o último.

## Ao consolidar

Apresente os dois pareceres lado a lado, com o veredito de cada um. Se divergirem no
veredito, diga isso explicitamente em vez de escolher um.
