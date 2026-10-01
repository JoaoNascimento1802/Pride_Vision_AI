---
description: Roda o gate completo (pytest, ruff, mypy, vitest, build, rastreabilidade) e relata
---

Rode o gate único do projeto e relate o resultado.

```powershell
.\scripts\verificar.ps1
```

Em ambiente POSIX:

```bash
./scripts/verificar.sh
```

## O que ele roda

| Etapa | Comando |
|---|---|
| Suíte do backend | `python -m pytest -q` |
| Lint do backend | `python -m ruff check app/ tests/` |
| Tipos do backend | `python -m mypy --strict app/` |
| Testes do frontend | `npm run test` |
| Build do frontend | `npm run build` |
| Rastreabilidade AC ↔ teste | `python scripts/rastreabilidade.py --emitir` |

Não aborta no primeiro erro de propósito — um ruff vermelho não pode esconder o resultado
da suíte.

## Ao relatar

- Mostre o resumo com o resultado de cada etapa.
- Para cada falha: o erro real, não uma paráfrase.
- **Não** conserte nada por iniciativa própria. Reporte e pergunte, salvo se o usuário já
  tiver pedido a correção.
- Se a rastreabilidade reprovar, liste os ACs órfãos — é a lista de trabalho do Robert.

Gate vermelho significa que a tarefa **não** está concluída. Não relate como concluída.

Argumentos: $ARGUMENTS (use `-Rapido` para pular o build do frontend durante a
implementação — nunca para fechar tarefa).
