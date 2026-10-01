# PRIDE Vision AI — Audit Log (Trilha de Auditoria)

## 15.1. Armazenamento e Mascaramento

- **AC-AUDIT-01** — Mascaramento de dados sensíveis.
  - **Dado** um payload de requisição contendo "password", "token", "secret" (mesmo aninhados)
  - **Quando** o AuditService registra a ação
  - **Então** os valores sensíveis devem ser substituídos por `[REDACTED]` no banco de dados.

- **AC-AUDIT-02** — Imutabilidade da trilha.
  - **Dado** um registro no AuditLog
  - **Quando** o usuário tentar deletar ou atualizar via API REST
  - **Então** a operação não deve existir (404/405), garantindo append-only.

## 15.2. Captura de Eventos Core

- **AC-AUDIT-03** — Registro de Login e Logout.
  - **Dado** uma tentativa de login (sucesso ou falha) ou logout
  - **Quando** a ação for processada
  - **Então** um evento `LOGIN_SUCCESS`, `LOGIN_FAILURE` ou `LOGOUT` deve ser registrado no AuditLog sem expor a senha.

- **AC-AUDIT-04** — Ações de Vulnerabilidades e Políticas.
  - **Dado** a criação/atualização de uma Vulnerabilidade ou Policy
  - **Quando** a ação for concluída
  - **Então** deve gerar um AuditLog contendo o ID da entidade e o Action correspondente.

- **AC-AUDIT-05** — Ações de CI/CD e Ticketing.
  - **Dado** a execução de um Security Gate ou sincronização de Ticket
  - **Quando** a ação terminar
  - **Então** a plataforma deve registrar o evento (e.g. `GATE_EXECUTED`, `SYNC_TICKET`) e os dados não sensíveis do payload.

## 15.3. Acesso e Paginação

- **AC-AUDIT-06** — Paginação.
  - **Dado** uma requisição `GET /api/audit`
  - **Quando** o usuário enviar parâmetros `skip` e `limit`
  - **Então** a API deve retornar uma lista paginada e a contagem total de itens.

- **AC-AUDIT-07** — RBAC de Auditoria.
  - **Dado** um usuário com permissão `AUDIT_READ` (ex: ADMIN, AUDITOR)
  - **Quando** requisitar os eventos de auditoria
  - **Então** a lista deve ser retornada, mas usuários sem a permissão devem receber HTTP 403.

