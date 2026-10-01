# Convenções de teste — backend

> Regra-fonte: `AGENTS.md` #1 e #2. Aqui está só o *como escrever*.

## Todo teste cita um AC

O vínculo entre a especificação e o código é literal: o ID do AC aparece no texto do
teste. É isso que `scripts/rastreabilidade.py` lê.

```python
def test_confirmacao_dupla_em_producao_exposta_e_critica() -> None:
    """AC-RISCO-01 — Semgrep e Nuclei confirmam em produção exposta → Crítico."""
```

O ID vai **no começo da docstring**, seguido de travessão e da frase que resume o
critério. Um teste pode citar mais de um AC quando cobre os dois de fato:

```python
    """AC-IA-03, AC-IA-04 — o texto enviado ao provedor não contém IP nem token."""
```

Em teste parametrizado, o ID vai no `id=` do caso — é o que aparece na saída do pytest:

```python
@pytest.mark.parametrize(
    ("ambiente", "esperado"),
    [
        pytest.param(Ambiente.PRODUCAO, Risco.CRITICO, id="AC-RISCO-01"),
        pytest.param(Ambiente.HOMOLOGACAO, Risco.ALTO, id="AC-RISCO-05"),
    ],
)
```

Quando uma classe inteira cobre um bloco de ACs, a docstring da classe pode listá-los —
mas só se **todos** os métodos dela contribuírem para aqueles ACs.

## Vermelho válido

Robert escreve o teste antes da implementação. O teste precisa falhar **pelo motivo
certo**:

- `AssertionError` no valor esperado: vermelho válido.
- `ImportError`/`AttributeError` porque a função ainda não existe: vermelho válido.
- `SyntaxError` no próprio teste: não é vermelho, é teste quebrado. Conserte.

## Onde cada coisa é testada

| Arquivo | Cobre |
|---|---|
| `test_risk_engine.py` | A matriz de risco pura — `AC-RISCO-*` |
| `test_services.py` | Normalização, correlação, masking — `AC-COR-*`, `AC-IA-*` de masking |
| `test_ingestion.py` | Parsers e persistência dos relatórios — `AC-ING-*` |
| `test_ai.py` | Contrato com OpenAI/Gemini e as proibições da IA — `AC-IA-*` |
| `test_applications.py` | CRUD e inventário — `AC-INV-*` |
| `test_vulnerabilities.py` | Listagem, detalhe e ciclo de status — `AC-STATUS-*` |
| `test_auth.py` | Login simples — `AC-LOGIN-*` |
| `test_infra.py` | Rotas de infraestrutura e arquitetura — `AC-ARQ-*` |
| `test_config.py` | Configuração e avisos de boot — `AC-ARQ-*` |

Teste que não cabe em nenhum desses arquivos provavelmente está cobrindo comportamento
que a SDD não descreve. Volte para `SDD/`.

## Isolamento

`conftest.py` dá a cada teste um SQLite **em memória** próprio, criado e destruído no
escopo do teste. Nenhum teste enxerga dado de outro e nada toca `pride_vision.db`.

- `db` — sessão isolada
- `client` — `TestClient` com o banco do teste injetado no lugar do global
- `usuario_cadastrado` / `auth` — credenciais e header `Authorization`
- `aplicacao_producao` — o contexto de maior risco da spec (produção + internet + alta)

Precisa de um cenário novo? Acrescente fixture no `conftest.py`, não monte banco na mão
dentro do teste.

## Nada de rede

Os testes de IA usam SDK simulado (`monkeypatch`), nunca chamada real. Um teste que
depende de chave de API ou de internet é um teste que vai falhar na máquina do colega.

## Rodar

```bash
cd backend && python -m pytest -q
```

```bash
cd backend && python -m pytest tests/test_risk_engine.py -q
```

```bash
python scripts/rastreabilidade.py
```
