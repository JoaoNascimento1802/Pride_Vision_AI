# PRIDE Vision AI — Relatório de Conclusão: SLA

## 1. Estado Encontrado na Auditoria
Antes da implementação, a auditoria revelou que o projeto já possuía uma base robusta para o ciclo de vida das vulnerabilidades. A entidade `Vulnerability` já armazenava campos de rastreamento (`status`, `risco`, `justificativa`, `historico`), e a infraestrutura básica (`AuditLog`, `Ticketing`, `RBAC`, `Dashboard`) estava funcional. No entanto, faltavam mecanismos para calcular, rastrear e alertar proativamente sobre o vencimento de prazos.

## 2. Componentes de SLA que já Existiam
- **Timestamps**: `identificada_em` (data da detecção), `assigned_at` (atribuição do owner) e `resolved_at` (resolução) já existiam no banco, mas não eram aplicados para SLAs.
- **Risk Engine**: Determinava o risco de cada vulnerabilidade (`CRITICO`, `ALTO`, `MEDIO`, `BAIXO`, `INFORMATIVO`).
- **Remediation Workflow**: Máquina de estados controlando o clico de vida da vulnerabilidade.
- **Audit Log**: Trilha de ações que poderia ser reutilizada para registrar violações de SLA.

## 3. Componentes Implementados

### Políticas (SlaPolicy)
Criada a camada `SlaPolicy` que mapeia deterministicamente o risco de uma vulnerabilidade para um prazo fixo:
- **CRÍTICO**: 5 dias
- **ALTO**: 15 dias
- **MÉDIO**: 30 dias
- **BAIXO**: 90 dias
- **INFORMATIVO**: 0 dias (Sem SLA)

### Serviço (SlaService)
Implementado `SlaService` para orquestrar os cálculos e as transições de SLA. 
- **Cálculo de Prazos (`calcular_estado`)**: Determina dinamicamente se a vulnerabilidade está `ON_TRACK`, `DUE_SOON`, `OVERDUE`, `COMPLETED` ou `PAUSED`.
- **Aging (`calcular_aging`)**: Identifica quantos dias a vulnerabilidade está ativa e se está vencida ou não, comparando `due_at` e `now`.

### Timestamps Adicionais
- **`due_at`**: Adicionado ao modelo `Vulnerability` para armazenar o prazo exato. Preenchido na criação da vulnerabilidade (ou seja, `identificada_em + sla_days`).

### Background Scheduler (Cron)
Implementado um scheduler assíncrono (`_sla_scheduler`) no `main.py` utilizando FastAPI background tasks, que roda periodicamente para verificar SLAs próximos do vencimento ou vencidos.

## 4. Como o SLA integra com a Remediation Workflow
O SLA funciona de maneira passiva, dependendo diretamente da **Máquina de Estados** (State Machine) existente:
- Se o status muda para `CORRIGIDA` ou `FALSO_POSITIVO`, o SLA considera como `COMPLETED` através do preenchimento de `resolved_at`.
- Se a vulnerabilidade é `ACEITO_COMO_RISCO` ou está bloqueada temporariamente, o estado do SLA muda para `PAUSED`.
- Quando um novo finding é gerado, o `due_at` é definido imediatamente.

## 5. Eventos e Notificações Idempotentes
A rotina de verificação no scheduler dispara eventos que são registrados no **Audit Log** (`AuditAction.SLA_BREACHED` e `AuditAction.SLA_DUE_SOON`).
- **Idempotência**: O sistema verifica antes no Audit Log se o alerta de `SLA_BREACHED` já foi enviado para aquela vulnerabilidade para não disparar notificações duplicadas.

## 6. Documentação Atualizada
Atualizado `ROADMAP_IMPLEMENTACAO.md` e test files. Testes unitários para todo o processo.

## 7. Próximo GAP Identificado Automaticamente
O próximo GAP mapeado na auditoria e visível no ROADMAP é a **Integração Real (Ticketing)**. Atualmente, o módulo de Ticketing está "Mockado (Jira)". A próxima etapa será substituir a abstração mockada pela implementação real de OAuth/API para o provedor (como Jira ou ServiceNow).
