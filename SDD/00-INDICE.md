# SDD — índice

> A especificação do PRIDE Vision AI, decomposta em critérios de aceitação numerados.
> **Fonte:** `SDD/anexos/PRIDE-Vision-AI.pdf` (intocado) e `SDD/anexos/spec-extraida.txt`
> (o mesmo texto, extraído, para poder ser lido por ferramenta e citado por seção).
>
> Regra-fonte do processo: `AGENTS.md`. Como escrever spec nova: `SDD/templates/SPEC_TEMPLATE.md`.

## Para X, leia Y

| Preciso de… | Documento | Prefixo dos ACs |
|---|---|---|
| O fluxo ponta a ponta e o que a plataforma **não** é | `01-visao-geral.md` | `AC-FLUXO` |
| Cadastro de aplicações e contexto de negócio | `02-inventario.md` | `AC-INV` |
| Upload e leitura dos relatórios Semgrep/Nuclei | `03-ingestao.md` | `AC-ING` |
| O que conta como *match* entre as duas ferramentas | `04-correlacao.md` | `AC-COR` |
| A matriz de risco e os cinco fatores | `05-risco.md` | `AC-RISCO` |
| O que a IA pode, o que não pode e o mascaramento | `06-ia.md` | `AC-IA` |
| Os cinco status e o ciclo de tratamento | `07-acompanhamento.md` | `AC-STATUS` |
| As quatro telas e seus campos | `08-interface.md` | `AC-UI` |
| Stack, arquitetura, login e configuração | `09-arquitetura.md` | `AC-ARQ`, `AC-LOGIN` |
| Os onze itens do MVP e onde cada um foi coberto | `10-mvp.md` | — (referencia os demais) |
| CI/CD Security Gates, políticas, exceções e histórico de gate | `11-ci-security-gates.md` | `AC-CI` |
| Quais ACs têm teste hoje | `RASTREABILIDADE.md` | — (gerado) |

## Mapa PDF → SDD

| Seção do PDF | Documento |
|---|---|
| §1 Ideia do projeto | `01-visao-geral.md` |
| §2 Problema | `01-visao-geral.md` |
| §3 Como o sistema funcionará | `01-visao-geral.md`, `03-ingestao.md` |
| §4.1 Inventário de aplicações | `02-inventario.md` |
| §4.2 Centralização dos achados | `03-ingestao.md`, `08-interface.md` |
| §4.3 Priorização baseada em risco | `05-risco.md` |
| §4.4 Acompanhamento da correção | `07-acompanhamento.md` |
| §5 Regra de risco | `05-risco.md` |
| §6 Como funcionará a IA | `06-ia.md` |
| §7 Interface e telas | `08-interface.md` |
| §8 Tecnologias | `09-arquitetura.md` |
| §9 Arquitetura simplificada | `09-arquitetura.md` |
| §10 Escopo do MVP | `10-mvp.md` |
| §12 Divisão do grupo | — (organização da equipe, não requisito de produto) |
| §13 Roadmap de produção | — (ordem de execução, não requisito de produto) |
| §14 Definição final | `01-visao-geral.md` |

## Convenções

**ID:** `AC-<PREFIXO>-<nn>`. Casos de borda usam `E` antes do número: `AC-INV-E1`.

**Formato:** Dado / Quando / Então. Se não dá para escrever assim, não é critério
testável — é intenção, e intenção não entra na SDD.

**`[extensão]`:** marca o AC que **não** vem do PDF. A especificação é curta e deixa
lacunas; preenchê-las é legítimo, esconder que foram preenchidas não é. Todo AC marcado
assim é decisão de projeto, e o usuário pode derrubá-la.

**`[proibição]`:** marca o AC que descreve algo que o sistema **não** pode fazer. São tão
testáveis quanto os outros e costumam ser os mais importantes — a §6 do PDF é quase toda
feita deles.

## O gate

```bash
python scripts/rastreabilidade.py
```

Falha quando: um AC não tem teste, um teste cita AC que não existe, ou um AC está sem
texto. Enquanto ele estiver vermelho, a entrega não está pronta — sem exceção e sem
"depois eu escrevo o teste".
