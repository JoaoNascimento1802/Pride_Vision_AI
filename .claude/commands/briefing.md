---
description: Abertura de sessão — regras ativas, estado do gate e o que atacar primeiro
---

Briefing de abertura. Execute e apresente; **não** inicie implementação.

## Passos

1. **Ler as regras** (em paralelo):
   - `AGENTS.md` — regras inegociáveis, fonte única
   - `CLAUDE.md` — contrato operacional

2. **Estado do gate**:

   ```bash
   python scripts/rastreabilidade.py
   ```

   ```bash
   cd backend && python -m pytest -q
   ```

   O gate completo (`.\scripts\verificar.ps1`) só se o usuário pedir — ele roda build de
   frontend e leva tempo.

3. **Situação da SDD**: liste os documentos de `SDD/` e, para cada um, quantos ACs têm
   teste. `SDD/RASTREABILIDADE.md` já traz isso pronto, se estiver atualizado.

4. **Decisões pendentes**: confira a seção "Divergências com o PDF — decisão pendente" em
   `SDD/05-risco.md`. Divergência aberta é trabalho não fechado.

## Formato de saída

```
## Regras ativas
<as regras inegociáveis do AGENTS.md, verbatim — não resumir, não filtrar>

## Estado do gate
| Etapa | Resultado |
|---|---|
| pytest | X passando |
| rastreabilidade | Y/Z ACs com teste |

## SDD
| Documento | ACs | Com teste | Órfãos |
|---|---|---|---|

## Decisões pendentes do usuário
| # | Assunto | Onde |
|---|---|---|

## Recomendação
<o que atacar primeiro e por quê — considere: ACs órfãos antes de feature nova, divergência
aberta antes de extensão>
```

## Regras

- Nunca inicie implementação no briefing. Apresente e aguarde a decisão.
- Se o gate estiver vermelho, isso vem antes de qualquer tarefa nova — diga isso.
- Não resuma as regras do `AGENTS.md`. Elas são curtas de propósito e valem verbatim.
