---
description: Robert deriva os testes de um ou mais ACs da SDD — vermelhos, antes da implementação
---

Delegue ao agent **robert-zane**: derivar os testes dos critérios de aceitação indicados,
**antes** de qualquer implementação.

ACs a cobrir: $ARGUMENTS

Sem argumento, cubra os ACs órfãos que o gate apontar:

```bash
python scripts/rastreabilidade.py
```

## Passos

1. **Ler os ACs** nos documentos de `SDD/`. Se algum precisa de teste e não tem AC, isso é
   spec incompleta — devolva para Harvey em vez de inventar critério.

2. **Escrever um teste por AC**, no mínimo, seguindo `backend/tests/CLAUDE.md` (backend) ou
   `frontend/CLAUDE.md` (telas). O ID no começo da docstring:

   ```python
   def test_algum_comportamento() -> None:
       """AC-XXX-01 — <o critério em uma linha>."""
   ```

   Parametrizado: o ID vai no `id=` do `pytest.param`. Frontend: no nome do `it(...)`.

3. **Rodar e confirmar o vermelho**, pelo motivo certo:
   - vermelho válido: `AssertionError`, `ImportError`, `AttributeError`
   - vermelho inválido: `SyntaxError` no próprio teste

   ```bash
   cd backend && python -m pytest -q
   ```

4. **Reportar** a tabela AC ↔ teste ↔ motivo do vermelho, e parar. A implementação é de
   Louis ou Mike, não sua.

## Regras

- Um teste que nasce **verde** não provou nada. Ou o comportamento já existia — e aí diga
  isso claramente, é um AC retroativo cobrindo código que já funciona — ou o teste está
  errado.
- Nada de rede. IA se testa com SDK simulado.
- Não implemente para o teste passar. Esse não é o seu passo.
