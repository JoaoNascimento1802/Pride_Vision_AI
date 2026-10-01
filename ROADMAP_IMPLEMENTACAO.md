# PRIDE Vision AI â€” Roadmap e Estado de ImplementaÃ§Ã£o

> **Atualizado em:** 2026-09-19
> **Status Geral do Gate:** âœ… VERDE

Este documento atua como a fonte central da verdade sobre o estado de desenvolvimento do PRIDE Vision AI. Ele reflete o que **realmente existe no cÃ³digo e foi validado**, diferindo do roadmap original que indica o cenÃ¡rio ideal planejado.

---

## 1. Resumo atual

O PRIDE Vision AI encontra-se com o MVP de *Application Security Posture Management* (ASPM) consolidado. Ele atualmente integra relatÃ³rios SAST, DAST, SCA, IaC e Secrets, aplica correlaÃ§Ã£o, determina o nÃ­vel de risco baseado no contexto de negÃ³cio, orquestra portÃµes de seguranÃ§a (Security Gates) em fluxos de CI/CD, e gerencia controle de acesso via RBAC. 

O prÃ³ximo passo prioritÃ¡rio na evoluÃ§Ã£o do projeto Ã© a **expansÃ£o da capacidade de Container Scanning**, estendendo a infraestrutura atual que jÃ¡ lÃª o scanner Trivy (usado para SCA) para cobrir informaÃ§Ãµes focadas na estrutura das imagens (Layers, Digests, Base Images).

---

## 2. Estado geral

| MÃ³dulo | Status | Backend | Frontend | Banco | Testes | IntegraÃ§Ã£o | ObservaÃ§Ãµes |
|---|---|---|---|---|---|---|---|
| Authentication | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | JWT com controle de sessÃ£o. |
| Inventory | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Cadastro de aplicaÃ§Ãµes e contextos (Ambiente/ImportÃ¢ncia). |
| SAST | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | Semgrep | Parseia regra, arquivo, linha, CWE. |
| DAST | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | Nuclei | Parseia template, url, status, evidÃªncia. |
| SCA | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | Trivy | Parseia pacote, CVE e severidade. |
| Secrets | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | Gitleaks | Parseia fingerprint e repositÃ³rio. |
| SBOM | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | SPDX/CycloneDX | ImportaÃ§Ã£o, listagem e detalhamento de pacotes. |
| IaC | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | Checkov | Parseia infra as code misconfigurations. |
| Container | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | Trivy (Container) | Parseia image, digest, tag, layers, dependÃªncias de OS. |
| Findings | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Entidade `AchadoNormalizado` e gravada como `Finding`. |
| Normalization | âœ… IMPLEMENTADO | âœ… | N/A | N/A | âœ… | N/A | Converte schemas diversos num vocabulÃ¡rio central. |
| Deduplication | âœ… IMPLEMENTADO | âœ… | N/A | N/A | âœ… | N/A | Evita duplicaÃ§Ã£o do mesmo achado. |
| Correlation | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Funde SAST e DAST confirmando risco real. |
| Risk Engine | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Classifica CrÃ­tico, Alto, MÃ©dio, Baixo sem IA. |
| SLA | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Status histÃ³rico, rÃ©guas de prazo, aging, notificaÃ§Ã£o e dashboard integrados. |
| Remediation | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Status da vulnerabilidade, mas workflow manual. |
| Remediation | ðŸŸ¢ IMPLEMENTADO | ðŸŸ¢ | ðŸŸ¢ | ðŸŸ¢ | ðŸŸ¢ | N/A | State machine completa de transiÃ§Ãµes e SLA. |
| Ticketing | ðŸŸ¡ PARCIALMENTE IMPLEMENTADO | âœ… | âŒ | âœ… | âœ… | Mock (Jira) | API pronta e mockada; falta integraÃ§Ã£o real (OAuth). |
| RBAC/AuthZ | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | 6 perfis, controle fino de endpoints. |
| Policies | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Regras de bloqueio e warns, com exclusÃµes. |
| Security Gate | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Analisa policies e gera decisÃ£o determinÃ­stica. |
| CI/CD | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Registra pipelines e roda gate. |
| PR/MR Feedback | âœ… IMPLEMENTADO | âœ… | N/A | N/A | âœ… | GitHub/GitLab | Webhooks postam comentÃ¡rios de bloqueio em PRs. |
| Audit Log | âœ… IMPLEMENTADO | âœ… | âœ… | âœ… | âœ… | N/A | Trilha de auditoria centralizada para acessos e aÃ§Ãµes com imutabilidade. |
| AI | âœ… IMPLEMENTADO | âœ… | âœ… | N/A | âœ… | AI Provider | Assiste no entendimento de bugs, nÃ£o toma aÃ§Ã£o. |
| Dashboard | âœ… IMPLEMENTADO | âœ… | âœ… | N/A | âœ… | N/A | MÃ©tricas globais consolidadas. |
| API Security | ✅ IMPLEMENTADO | ✅ | ✅ | N/A | ✅ | Scanner Local (httpx) | Implementado parsing OpenAPI e DAST (Passive/Active) integrados. |
| Runtime | âšª AUSENTE | âŒ | âŒ | âŒ | âŒ | N/A | NÃ£o iniciado. |
| Cloud | âšª AUSENTE | âŒ | âŒ | âŒ | âŒ | N/A | Checkov atende parte de IaC, mas CSPM real nÃ£o. |
| Supply Chain | âšª AUSENTE | âŒ | âŒ | âŒ | âŒ | N/A | NÃ£o iniciado. |
| Compliance | âšª AUSENTE | âŒ | âŒ | âŒ | âŒ | N/A | NÃ£o iniciado. |
| Observability | âšª AUSENTE | âŒ | âŒ | âŒ | âŒ | N/A | NÃ£o iniciado. |

---

## 3. Funcionalidades concluÃ­das

### 1. InventÃ¡rio de AplicaÃ§Ãµes
- **Objetivo**: Cadastro base que fornece contexto (Ambiente, ImportÃ¢ncia e ExposiÃ§Ã£o) para o Risk Engine.
- **Implementado**: Backend (CRUD), Banco (`Application`), Frontend (Lista e formulÃ¡rios).
- **Testes e IntegraÃ§Ã£o**: Coberto nos testes E2E do frontend e routers backend.

### 2. IngestÃ£o Normalizada de SAST, DAST, SCA, Secrets e IaC
- **Objetivo**: Receber relatÃ³rios brutos variados e reduzi-los a uma estrutura unificada.
- **Implementado**: Parser isolado (`normalizer.py`) para Semgrep, Nuclei, Trivy (como SCA), Gitleaks e Checkov. 
- **Testes**: 100% testado na camada de parsing; sem chamadas de rede reais.

### 3. CorrelaÃ§Ã£o e Risk Engine
- **Objetivo**: Determinar risco real (CrÃ­tico, Alto, MÃ©dio, Baixo) usando contexto da aplicaÃ§Ã£o e correlaÃ§Ã£o.
- **Implementado**: `correlator.py` une SAST + DAST. `risk_engine.py` cruza risco tÃ©cnico com ambiente/exposiÃ§Ã£o.

### 4. RBAC e AutenticaÃ§Ã£o
- **Objetivo**: Controlar o acesso e visibilidade.
- **Implementado**: AutenticaÃ§Ã£o com JWT, `Role` (Admin, AppSec, Developer, Tech Lead, Manager, Auditor), decoradores `RequirePermission`.

### 5. Security Gates e CI/CD
- **Objetivo**: Integrar no pipeline de desenvolvimento, barrando deploys de alto risco.
- **Implementado**: Endpoints `/api/ci/check` e gerador de feedback real (`github.py`, `gitlab.py`) em PRs.

### 6. IA Assistiva
- **Objetivo**: Explicar vulnerabilidades sem conceder Ã  IA poder de decisÃ£o ou manipulaÃ§Ã£o.
- **Implementado**: `ai_explainer.py` isolado da tomada de decisÃ£o. Mascaramento em `data_masker.py` protege PII/Secrets.

---

## 4. Funcionalidades parciais

### Ticketing
- **O que jÃ¡ existe**: Endpoint de criaÃ§Ã£o de tickets (`/api/tickets`), estrutura no banco `Ticket`.
- **O que falta**: ComunicaÃ§Ã£o real com a API do Jira, GitHub Issues, etc. Atualmente ele roda sobre um mock.
- **PrÃ³ximo passo**: Adicionar OAuth ou credenciais por projeto para comunicaÃ§Ã£o verdadeira com JIRA.

### SLA e Remediation
- **O que jÃ¡ existe**: Modelagem de status, ciclo de vida com state machine, rÃ©guas de SLA e scheduler background de checagem implementados e totalmente funcionais.
- **O que falta**: Integrar SLA com relatÃ³rios de performance (SLA Metrics).
- **PrÃ³ximo passo**: Configurar relatÃ³rios de conformidade.

---

## 5. Problemas conhecidos e dÃ©bitos tÃ©cnicos

| Problema | Severidade | MÃ³dulo afetado | Causa | Impacto | SoluÃ§Ã£o planejada | Status |
|---|---|---|---|---|---|---|
| Acoplamento de Categorias Trivy | P2 â€” MÃ©dia | IngestÃ£o | O Trivy Ã© usado para SCA, porÃ©m o json schema dele tambÃ©m faz Container Scanning. O cÃ³digo forÃ§ou "SCA". | Achados de container serÃ£o categorizados equivocadamente se recebidos sem preparo de estrutura de model de imagens. | Reescrever/Estender `ler_trivy` baseado na flag `ArtifactType`. | ðŸ”µ PLANEJADO |

---

## 6. Gap Analysis consolidado

| Funcionalidade | Estado Atual | Estado Esperado | Gap | Prioridade | PrÃ³xima AÃ§Ã£o |
|---|---|---|---|---|---|
| Container Scanning | âœ… IMPLEMENTADO | âœ… IMPLEMENTADO | Resolvido (Parser, model e UI funcionais) | - | - |
| IntegraÃ§Ã£o Real Jira | ðŸŸ¡ PARCIALMENTE IMPLEMENTADO | âœ… IMPLEMENTADO | Fluxo OAuth / Token real | P1 â€” Alta | Implementar provider Jira real. |
| Supply Chain Sign | âšª AUSENTE | âœ… IMPLEMENTADO | ValidaÃ§Ã£o de assinatura de imagens e SBOM | P2 â€” MÃ©dia | Adicionar Valint ou Sigstore parser. |

---

## 7. Arquitetura atual

A arquitetura atual segue um fluxo estrito e determinÃ­stico de ingestÃ£o:

```text
Upload (JSON) â†’ Endpoint â†’ Ingestion Service
```
```text
Ingestion Service â†’ Normalizer (Parser) â†’ AchadoNormalizado
```
```text
Ingestion Service â†’ Deduplicator / Correlator â†’ GrupoCorrelacionado
```
```text
Risk Engine (Contexto + Severidade) â†’ ClassificaÃ§Ã£o (CrÃ­tico..Baixo) â†’ Database (Vulnerability + Finding)
```
```text
Pipeline / CI â†’ Security Gate â†’ Policy Engine â†’ AvaliaÃ§Ã£o (PASS/WARN/BLOCK) â†’ PR/MR Feedback Service
```

A IA nunca entra no fluxo acima. Ela Ã© uma ramificaÃ§Ã£o *read-only* acionada sob demanda pelo usuÃ¡rio.

---

## 8. Backend

- **Framework**: FastAPI + SQLAlchemy + SQLite (desenhado agnÃ³stico para Postgres).
- **Routers**: MÃ³dulos divididos logicamente (`applications`, `uploads`, `vulnerabilities`, `auth`, `ci`, `dashboard`, etc).
- **Services**: LÃ³gica pura sem banco de dados misturada nas entranhas. `dominio.py` rege os modelos sem ORM.
- **Security**: Decoradores e Middlewares protegem endpoints baseados no papel (`RBAC`).

---

## 9. Frontend

- **Framework**: React + Vite + TypeScript + Tailwind.
- **Pages**: `Aplicacoes`, `Dashboard`, `Login`, `Vulnerabilidades`, `DetalheVulnerabilidade`, `CiCdSecurity`.
- **Integrations**: Autenticado via Context API e axios interceptors.

---

## 10. Banco de dados

- **Database**: SQLite configurado no `app.database`.
- **Principais entidades**: `Application`, `Upload`, `Finding`, `Vulnerability`, `Policy`, `Sbom`, `PipelineRun`.
- **Relacionamentos**: Fortemente amarrados com `CASCADE` (deletar App deleta findings, policies, uploads, etc).

---

## 11. Scanners suportados

| Nome | Formato | Parser | Status | ObservaÃ§Ãµes |
|---|---|---|---|---|
| Semgrep | JSON | `ler_semgrep` | âœ… IMPLEMENTADO | SAST (cÃ³digo). |
| Nuclei | JSONL | `ler_nuclei` | âœ… IMPLEMENTADO | DAST (URL/runtime). |
| Trivy | JSON | `ler_trivy` | âœ… IMPLEMENTADO | SCA (apenas lib/dependencies por enquanto). |
| Checkov | JSON | `ler_checkov` | âœ… IMPLEMENTADO | IaC (misconfigs). |
| Gitleaks | JSON | `ler_gitleaks` | âœ… IMPLEMENTADO | Secrets. |

---

## 12. Pipeline de Findings

1. **Import** -> O router autoriza a rota `POST /api/aplicacoes/{id}/uploads/{scanner}`.
2. **Parser/Normalization** -> Retorna Dataclasses congeladas `AchadoNormalizado`.
3. **Deduplication** -> Agrupa e compara hash (endpoint, tipo, CVE, etc).
4. **Correlation** -> Une evidÃªncias complementares (ex: Semgrep detectou X, Nuclei confirmou na URL Y).
5. **Risk Engine** -> Calcula o `Risco` com base no `Ambiente` da App.

---

## 13. Risk Engine

100% determinÃ­stico. Sem inteligÃªncia artificial. Avalia cruzando:
- ImportÃ¢ncia da aplicaÃ§Ã£o (Alta, MÃ©dia, Baixa)
- ExposiÃ§Ã£o (Internet, Interna)
- Ambiente (ProduÃ§Ã£o, Teste, etc)
- Severidade tÃ©cnica gerada pelo scanner
- Fatores agravantes (como DAST confirmar um risco SAST).

---

## 14. Policy Engine

Permite aos administradores criar regras em duas categorias (Global, Por AplicaÃ§Ã£o). Define bloqueios ou avisos se a severidade (base ou customizada) cruzar o limite configurado (ex: Bloquear tudo que for "CrÃ­tico"). Trabalha tambÃ©m com "ExceÃ§Ãµes temporÃ¡rias".

---

## 15. Security Gate

A API consumida pela pipeline de CI/CD. Retorna `PASS`, `WARN` ou `BLOCK`. Idempotente (salva logs de avaliaÃ§Ãµes passadas e vincula por `commit_sha`).

---

## 16. CI/CD

Modelos prontos que registram a execuÃ§Ã£o no repositÃ³rio. O feedback atua via Webhooks ou APIs do GitLab e GitHub gravando o comentÃ¡rio de retorno de bloqueio/aviso diretamente no Pull Request.

---

## 17. Ticketing

O sistema gerencia o estado da Vulnerabilidade (`NOVA`, `EM_ANALISE`, `EM_CORRECAO`, `CORRIGIDA`), porÃ©m a chamada para API externa (Jira) ainda retorna sucesso mockado.

---

## 18. RBAC/AuthZ

A autorizaÃ§Ã£o em nÃ­vel de objeto evita que um `Developer` possa aprovar exceÃ§Ãµes de `AppSec` ou modificar `Policies` de CI/CD. A implementaÃ§Ã£o utiliza `fastapi.Depends`.

---

## 19. IA

O uso da LLM estÃ¡ contido no serviÃ§o `ai_explainer.py`. Passa invariavelmente pelo `data_masker.py` que substitui hashes, tokens e senhas antes de enviar a dÃºvida Ã  IA. Suas respostas sÃ£o entregues Ã  UI como "Dica", nunca como decisÃ£o automatizada.

---

## 20. IntegraÃ§Ãµes

| IntegraÃ§Ã£o | Provider | Status | Real/Mock | Configurada? | ObservaÃ§Ãµes |
|---|---|---|---|---|---|
| Trivy | Scanner | âœ… IMPLEMENTADO | Real | Sim | SCA funcionando. Container pendente. |
| Checkov | Scanner | âœ… IMPLEMENTADO | Real | Sim | Integrado ao pipeline unificado. |
| Gitleaks | Scanner | âœ… IMPLEMENTADO | Real | Sim | Integrado ao pipeline unificado. |
| GitHub | CI/CD PR | âœ… IMPLEMENTADO | Real | N/A | Provider e endpoints de webhook com HMAC. |
| GitLab | CI/CD MR | âœ… IMPLEMENTADO | Real | N/A | Provider desenhado, semelhante ao GitHub. |
| Jira | ITSM | ðŸŸ¡ PARCIALMENTE IMPLEMENTADO | Mock | NÃ£o | Endpoint escrito, requisiÃ§Ã£o remota mockada. |

---

## 21. Testes e qualidade

MÃ©tricas da Ãºltima execuÃ§Ã£o do Pipeline de SeguranÃ§a / Gate de Qualidade do cÃ³digo fonte do PRIDE:

- **Backend tests:** 413 testes passando (Pytest).
- **Frontend tests:** 41 testes passando (Vitest).
- **Ruff (Lint):** 0 erros.
- **Mypy:** 0 erros (Strict em 53 arquivos).
- **Build Frontend:** Sucesso (tsc + vite).
- **Rastreabilidade SDD:** 237/237 (Aprovado, todo critÃ©rio mapeado em PDF tem um teste).

---

## 22. Ãšltimo gate

- **Data**: 2026-09-19
- **Comando**: `scripts/verificar.ps1`
- **Resultado**: âœ… GREEN
- **Coverage Backend**: ~93%
- **Rastreabilidade**: âœ… Aprovada.

---

## 23. HistÃ³rico de implementaÃ§Ã£o

1. Setup inicial e repositÃ³rio.
2. AutenticaÃ§Ã£o e RBAC.
3. IngestÃ£o e Parser (Semgrep e Nuclei).
4. InventÃ¡rio e Dashboard.
5. CorrelaÃ§Ã£o de SAST e DAST e Risk Engine determinÃ­stico.
6. IA Assistiva e Mascaramento de dados.
7. SBOM Parsing (CycloneDX e SPDX).
8. IntegraÃ§Ã£o Trivy (SCA) e Gitleaks (Secrets).
9. MÃ³dulo CI/CD Security Gates e PR/MR Feedback.
10. IaC Scanning com Checkov.

---

## 24. PrÃ³ximas etapas

A priorizaÃ§Ã£o foi elaborada mapeando as lacunas com o pipeline de seguranÃ§a padrÃ£o de mercado:

1. **P1 â€” Container Scanning (PrÃ³xima etapa ativa)**: IngestÃ£o de `ContainerImage`, camadas e vulnerabilities cruzadas (Trivy ArtifactType=container_image).
2. **P2 â€” IntegraÃ§Ã£o Ticketing (Jira/GitLab Real)**: EfetivaÃ§Ã£o do payload OAuth e chamadas de fato na API.
3. **P3 â€” Supply Chain / Assinatura**: Adicionar atestados de proveniÃªncia para validar se a imagem do SBOM foi construÃ­da pela pipeline oficial.

---

## 25. Roadmap futuro

**Fase 1: FundaÃ§Ã£o / MVP (ATUALMENTE CONCLUÃDA)**
- InventÃ¡rio, SAST, DAST, SCA, Secrets, IaC, Risk Engine.

**Fase 2: Cobertura de desenvolvimento (EM ANDAMENTO)**
- CI/CD Gates, PR Feedback, Container Scanning.

**Fase 3: Infraestrutura e Supply Chain**
- SBOM detalhado em tempo de runtime, ValidaÃ§Ã£o de Assinaturas (Sigstore).

**Fase 4: Runtime, Cloud e APIs**
- CSPM Cloud Posture e monitoramento eBPF.

**Fase 5: Plataforma corporativa**
- RelatÃ³rios avanÃ§ados executivos, IntegraÃ§Ã£o SSO Empresarial.

---

## 26. CritÃ©rios para considerar cada etapa concluÃ­da

- 100% dos ACs escritos no diretÃ³rio `SDD/`.
- Todos os testes no estado PASS (`pytest` e `vitest`).
- O gate restrito (`verificar.ps1`) executando 100% verde (sem lints ou quebra de tipos).
- IntegraÃ§Ã£o funcional, desde a UI (React) atÃ© a persistÃªncia (DB).
- Arquivos modificados unitariamente sem quebrar mÃ³dulos anteriores.

