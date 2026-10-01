# 17. SLA e Gestão de Prazos

Este documento detalha os critérios de aceite para a gestão de SLAs de vulnerabilidades.

## 17.1. Regras de Cálculo e Status
- **AC-SLA-01** — Cálculo da data limite (Due Date). **Dado** que uma nova vulnerabilidade foi identificada, **Quando** o SLA for calculado, **Entao** a data limite deve seguir a política definida por severidade, e o status será IN_SLA.
- **AC-SLA-02** — Transição para Due Soon. **Dado** uma vulnerabilidade com SLA ativo, **Quando** faltarem menos de N dias para o vencimento, **Entao** o status do SLA deve mudar para DUE_SOON.
- **AC-SLA-03** — Transição para Overdue (SLA Vencido). **Dado** uma vulnerabilidade aberta, **Quando** a data atual ultrapassar o Due Date, **Entao** o status do SLA deve mudar para OVERDUE e notificar.
- **AC-SLA-04** — Resolução de SLA. **Dado** uma vulnerabilidade em correção, **Quando** o status mudar para CORRIGIDA, **Entao** o SLA deve ser marcado como RESOLVED e o tempo total gasto deve ser registrado.
- **AC-SLA-05** — Recálculo ao mudar Risco. **Dado** uma vulnerabilidade, **Quando** seu Risco for alterado (ex: Alta para Crítica), **Entao** a Due Date deve ser recalculada e o status do SLA atualizado de acordo.

## 17.2. Exceções e Pausas
- **AC-SLA-06** — Estados de isenção e pausa. **Dado** que uma vulnerabilidade é marcada como FALSO_POSITIVO ou EXCECAO_TEMPORARIA, **Entao** o SLA deve ser considerado EXEMPT ou PAUSED.

## 17.3. Notificações e Eventos
- **AC-SLA-07** — Scheduler identifica SLA vencido e gera evento sem duplicar. **Dado** o processo em background, **Quando** o SLA vencer, **Entao** um evento de auditoria deve ser gerado garantindo idempotência.
