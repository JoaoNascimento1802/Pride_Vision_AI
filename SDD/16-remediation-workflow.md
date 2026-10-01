# 16. Remediation Workflow

## 16.1. Objetivo

Transformar o ciclo de status existente em um **workflow de remediação real e auditável**, adicionando:
máquina de estados com transições válidas, atribuição de responsável, comentários de remediação,
evidências de correção, fluxos de falso positivo, aceitação de risco, e preparação para SLA.

## 16.2. Contexto

O PRIDE já possui status, histórico e tickets. Esta seção formaliza as **regras de transição**,
adiciona os status ausentes (`AGUARDANDO_VALIDACAO`, `ACEITO_COMO_RISCO`, `EXCECAO_TEMPORARIA`,
`DUPLICADO`), e implementa o ciclo completo de remediação integrado ao Audit Log e ao RBAC existentes.

## 16.3. Máquina de Estados

Ciclo principal:
```
NOVA → EM_ANALISE → EM_CORRECAO → AGUARDANDO_VALIDACAO → CORRIGIDA
```

Fluxos alternativos:
```
NOVA | EM_ANALISE | EM_CORRECAO → FALSO_POSITIVO
NOVA | EM_ANALISE | EM_CORRECAO → ACEITO_COMO_RISCO
NOVA | EM_ANALISE → EXCECAO_TEMPORARIA
NOVA | EM_ANALISE | EM_CORRECAO → DUPLICADO
AGUARDANDO_VALIDACAO → EM_CORRECAO  (revalidação falhou)
CORRIGIDA → EM_CORRECAO  (reabertura)
```

Status encerrados (não mudam sem justificativa explícita):
- CORRIGIDA, FALSO_POSITIVO, ACEITO_COMO_RISCO, DUPLICADO

## 16.4. Critérios de Aceitação

- **AC-REM-01** — Máquina de estados. **Dado** uma vulnerabilidade em qualquer status, **Quando** uma transição inválida for tentada, **Entao** a API responde 422 com detalhe da transição proibida.

- **AC-REM-02** — Transição válida. **Dado** uma vulnerabilidade NOVA, **Quando** movida para EM_ANALISE, **Entao** o status é salvo e o histórico registrado com autor e data.

- **AC-REM-03** — Fluxo de correção completo. **Dado** uma vulnerabilidade EM_CORRECAO, **Quando** movida para AGUARDANDO_VALIDACAO, **Entao** o novo status é aceito.

- **AC-REM-04** — Revalidação aprovada. **Dado** uma vulnerabilidade AGUARDANDO_VALIDACAO, **Quando** movida para CORRIGIDA, **Entao** o resolved_at é preenchido automaticamente.

- **AC-REM-05** — Revalidação reprovada. **Dado** uma vulnerabilidade AGUARDANDO_VALIDACAO, **Quando** movida para EM_CORRECAO, **Entao** a transição é aceita e o histórico registrado.

- **AC-REM-06** — Reabertura. **Dado** uma vulnerabilidade CORRIGIDA, **Quando** movida para EM_CORRECAO, **Entao** a transição é aceita e o resolved_at é limpo.

- **AC-REM-07** — Owner/Assignee. **Dado** um usuário com finding:write, **Quando** chamar PATCH /{id}/owner, **Entao** o owner_id e owner_team são salvos e o assigned_at preenchido.

- **AC-REM-08** — Owner sem permissão. **Dado** um usuário sem finding:write, **Quando** tentar PATCH /{id}/owner, **Entao** a API responde 403.

- **AC-REM-09** — Comentário de remediação. **Dado** usuário autenticado com finding:read, **Quando** POST /{id}/comments com conteúdo, **Entao** o comentário é persistido com author_id e created_at.

- **AC-REM-10** — Listagem de comentários. **Dado** uma vulnerabilidade com comentários, **Quando** GET /{id}/comments, **Entao** todos os comentários são retornados em ordem cronológica.

- **AC-REM-11** — Sanitização de comentários. **Dado** um comentário com token ou senha, **Quando** armazenado, **Entao** o conteúdo não é mascarado (é texto do usuário, não payload automático), mas não é interpretado como HTML/JS.

- **AC-REM-12** — Evidência de correção. **Dado** usuário com finding:write, **Quando** POST /{id}/evidences com description e reference, **Entao** a evidência é persistida vinculada à vulnerabilidade.

- **AC-REM-13** — Listagem de evidências. **Dado** uma vulnerabilidade com evidências, **Quando** GET /{id}/evidences, **Entao** todas as evidências são retornadas.

- **AC-REM-14** — Falso positivo exige razão. **Dado** usuário com finding:close, **Quando** mudar status para FALSO_POSITIVO sem reason, **Entao** a API responde 422.

- **AC-REM-15** — Falso positivo com razão. **Dado** usuário com finding:close, **Quando** mudar status para FALSO_POSITIVO com reason, **Entao** o status é salvo e false_positive_reason é persistido.

- **AC-REM-16** — Aceitação de risco exige razão. **Dado** usuário com finding:close, **Quando** mudar status para ACEITO_COMO_RISCO sem reason, **Entao** a API responde 422.

- **AC-REM-17** — Aceitação de risco com razão. **Dado** usuário com finding:close, **Quando** mudar status para ACEITO_COMO_RISCO com reason, **Entao** o status é salvo, risk_acceptance_reason e risk_accepted_at são persistidos.

- **AC-REM-18** — Audit Log: status mudança. **Dado** qualquer mudança de status do workflow, **Quando** concluída, **Entao** o AuditLog registra actor, old_value, new_value e entity_id.

- **AC-REM-19** — Audit Log: owner. **Dado** mudança de owner, **Quando** concluída, **Entao** o AuditLog registra ASSIGNMENT_CHANGED com o owner anterior e novo.

- **AC-REM-20** — Audit Log: comentário. **Dado** adição de comentário, **Quando** concluída, **Entao** o AuditLog registra COMMENT_ADDED com o entity_id da vulnerabilidade.

- **AC-REM-21** — Audit Log: evidência. **Dado** adição de evidência, **Quando** concluída, **Entao** o AuditLog registra EVIDENCE_ADDED.

- **AC-REM-22** — RBAC comentários. **Dado** usuário sem autenticação, **Quando** POST /{id}/comments, **Entao** a API responde 401.

- **AC-REM-23** — SLA: campos de tempo. **Dado** uma vulnerabilidade CORRIGIDA, **Quando** consultada, **Entao** os campos detected_at e resolved_at estão presentes no payload.

- **AC-REM-24** — Novos status no vocabulário. **Dado** consulta às opções, **Quando** listados os status disponíveis, **Entao** AGUARDANDO_VALIDACAO e ACEITO_COMO_RISCO estão presentes.

- **AC-REM-25** — Detalhe inclui owner e times. **Dado** uma vulnerabilidade com owner, **Quando** o detalhe for consultado, **Entao** owner_id, owner_team e assigned_at são retornados.

## 16.5. Contrato de API

| Método | Rota | Corpo | Resposta | Erros |
|---|---|---|---|---|
| PATCH | `/api/vulnerabilidades/{id}/status` | `{status, comentario?, reason?}` | `VulnerabilidadeDetalhe` | 401, 403, 404, 409, 422 |
| PATCH | `/api/vulnerabilidades/{id}/owner` | `{owner_id?, owner_team?}` | `VulnerabilidadeDetalhe` | 401, 403, 404 |
| POST | `/api/vulnerabilidades/{id}/comments` | `{content}` | `CommentResponse` | 401, 404, 422 |
| GET | `/api/vulnerabilidades/{id}/comments` | — | `list[CommentResponse]` | 401, 404 |
| POST | `/api/vulnerabilidades/{id}/evidences` | `{description, reference?, evidence_type?}` | `EvidenceResponse` | 401, 403, 404, 422 |
| GET | `/api/vulnerabilidades/{id}/evidences` | — | `list[EvidenceResponse]` | 401, 404 |

## 16.6. RBAC

| Ação | Permissão mínima |
|---|---|
| Ver status, histórico, comentários | finding:read |
| Mudar status (abertos) | finding:write |
| Mudar status para encerrado (CORRIGIDA, FP, ACEITO_COMO_RISCO) | finding:close |
| Adicionar comentário | finding:read (autenticado) |
| Adicionar evidência | finding:write |
| Atribuir owner | finding:write |

## 16.7. Campos SLA (preparação)

Campos adicionados ao model Vulnerability para suporte futuro de SLA:
- `identified_at` (já existe como `identificada_em`)
- `assigned_at` — data da primeira atribuição
- `due_at` — prazo calculado (a ser preenchido quando SLA for implementado)
- `resolved_at` — data em que foi marcada como CORRIGIDA

## 16.8. Status

- [ ] Spec aprovada pelo usuário
- [ ] Testes escritos — vermelhos
- [ ] Implementação concluída — testes verdes
- [ ] `python scripts/rastreabilidade.py` verde
- [ ] Validação real executada

