# SDD — Escopo do MVP

## Origem

PDF §10 (Escopo do MVP).

## Contexto

> "O MVP precisa ter somente: […]"

Onze itens. A palavra "somente" é parte do requisito: o que não está nesta lista está fora
do escopo, e entra só como AC novo discutido antes. Este documento não cria ACs próprios —
ele é o **checklist de cobertura**, ligando cada item do MVP aos ACs que o provam.

## Os onze itens e onde cada um é coberto

| # | Item do MVP (§10) | Coberto por |
|---|---|---|
| 1 | Login simples | `AC-LOGIN-01` a `AC-LOGIN-08`, `AC-UI-30` a `AC-UI-32` |
| 2 | Cadastro de aplicações | `AC-INV-01` a `AC-INV-11`, `AC-UI-07` a `AC-UI-10` |
| 3 | Upload de `semgrep.json` | `AC-ING-01`, `AC-ING-06`, `AC-ING-09`, `AC-UI-11` |
| 4 | Upload de `nuclei.jsonl` | `AC-ING-02`, `AC-ING-07`, `AC-UI-11` |
| 5 | Leitura e organização dos dados | `AC-ING-03` a `AC-ING-05`, `AC-ING-08`, `AC-ING-12` |
| 6 | Comparação entre os resultados | `AC-COR-01` a `AC-COR-12` |
| 7 | Classificação de risco | `AC-RISCO-01` a `AC-RISCO-21` |
| 8 | Lista de vulnerabilidades | `AC-FLUXO-02`, `AC-UI-12` a `AC-UI-20` |
| 9 | Alteração do status de correção | `AC-STATUS-01` a `AC-STATUS-12`, `AC-UI-26`, `AC-UI-27` |
| 10 | Dashboard simples | `AC-UI-01` a `AC-UI-06`, `AC-STATUS-08` |
| 11 | Explicação por IA com dados mascarados | `AC-IA-01` a `AC-IA-22`, `AC-UI-25` |

## Os quatro pilares de ASPM (§4)

O PDF justifica o MVP dizendo que esse conjunto "já demonstra as principais características
de um ASPM". Os quatro pilares e onde estão:

| Pilar (§4) | Documento | Prova |
|---|---|---|
| 1. Inventário de aplicações | `02-inventario.md` | `AC-INV-01` |
| 2. Centralização dos achados | `03-ingestao.md`, `08-interface.md` | `AC-UI-12` a `AC-UI-18` |
| 3. Priorização baseada em risco | `05-risco.md` | `AC-RISCO-01` a `AC-RISCO-21` |
| 4. Acompanhamento da correção | `07-acompanhamento.md` | `AC-STATUS-01` a `AC-STATUS-12` |

## Fora do escopo

Registrado para que a resposta seja "não, e por quê" em vez de silêncio:

| Ideia | Por que está fora |
|---|---|
| Executar Semgrep ou Nuclei pela plataforma | PDF §3 é explícito: os arquivos chegam manualmente. Ver `AC-FLUXO-03`, `AC-FLUXO-04` |
| Outros scanners (Trivy, ZAP, Dependabot) | Exigiria parser novo; o MVP nomeia duas ferramentas |
| Multi-empresa / isolamento por tenant | "Login simples" no §10 — ver `09-arquitetura.md` |
| Papéis e permissões | Idem |
| Integração com Jira ou GitHub Issues | O PDF pede a **descrição** do ticket (`AC-IA-10`), não a abertura dele |
| A IA abrir PR ou corrigir código | Proibido pelo §6. Ver `AC-IA-13` a `AC-IA-17` |
| Notificação por e-mail ou webhook | Não consta no §10 |
| Migrações de banco (Alembic) | Não consta no §10 — ver restrição em `09-arquitetura.md` |
| Paginação e busca textual na lista | Não consta no §7 |
| Métricas históricas / tendência ao longo do tempo | A plataforma reflete a varredura atual, não a série histórica |

## Etapas do roadmap (§13) — situação

| Etapa | Situação |
|---|---|
| 1 — Preparar o projeto | Concluída |
| 2 — Backend básico (API, SQLite, cadastro, upload) | Concluída |
| 3 — Parsers | Concluída |
| 4 — Motor de risco | Concluída |
| 5 — Frontend (login, dashboard, aplicações, vulnerabilidades, detalhes) | Concluída |
| 6 — IA (masking, prompt, envio sanitizado, exibição) | Concluída |
| 7 — Acompanhamento (status, contagem) | Concluída |
| 8 — Integração final (conectar telas, testar fluxo, testar arquivos diferentes) | Em andamento — a prova é `scripts/verificar.ps1` verde e `RASTREABILIDADE.md` sem AC órfão |

## Status

- [x] Checklist conferido contra o PDF §10
- [x] Todos os ACs referenciados acima existem e têm teste (`python scripts/rastreabilidade.py`)
