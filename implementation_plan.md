# Audit Log Implementation Plan

This document outlines the approach for introducing a comprehensive, persistent, and queryable Audit Log to the PRIDE Vision AI platform, capturing WHO, WHAT, WHEN, and WHERE for all critical actions, adhering to RBAC, and masking sensitive data.

## User Review Required

> [!IMPORTANT]
> The list of critical actions mapped to the Audit Service covers the primary domains (Auth, Findings, Policies, Exceptions, Tickets, Security Gates). Let me know if there are any specific granular actions you'd like to prioritize beyond the ones listed in the prompt!
> The Audit Service will be injected via FastAPI `Depends`, which inherently requires endpoints to pass down the `AuditService` explicitly. We will avoid global singletons.

## Proposed Changes

### Database Layer

#### [NEW] `backend/app/models/audit_log.py`
Creates the SQLAlchemy ORM model for persistent logging.
- `id`: PK
- `actor_user_id`: ForeignKey to `users.id`
- `action`: String Enum
- `entity_type`: String Enum
- `entity_id`: String
- `old_value`: JSON (Nullable)
- `new_value`: JSON (Nullable)
- `metadata_info`: JSON (Nullable)
- `ip_address`: String
- `user_agent`: String
- `request_id`: String
- `criado_em`: DateTime

#### [MODIFY] `backend/app/models/enums.py`
- Add `AuditAction` enum (LOGIN, LOGOUT, CREATE_FINDING, CREATE_TICKET, RUN_SECURITY_GATE, etc).
- Add `EntityType` enum (USER, FINDING, POLICY, EXCEPTION, TICKET, PIPELINE, INTEGRATION, etc).

#### [MODIFY] `backend/app/models/__init__.py`
- Expose `AuditLog`, `AuditAction`, `EntityType` for SQLAlchemy metadata tracking.

---

### Service Layer

#### [NEW] `backend/app/services/audit.py`
Creates the `AuditService`.
- Exposes `log_action(...)` method.
- Contains sanitization utilities `sanitize_payload()` that masks `password`, `token`, `secret`, `authorization`, etc.

#### [NEW] `backend/app/schemas/audit.py`
- Pydantic schemas for `AuditLogResponse` and `PaginatedAuditLogResponse`.

---

### API Layer

#### [NEW] `backend/app/routers/audit.py`
- `GET /api/audit`: Returns a paginated list of audit events.
- Enforces `RequirePermission(Permission.AUDIT_READ)`.
- Supports filtering by `actor_user_id`, `action`, `entity_type`, `entity_id`.

#### [MODIFY] `backend/app/routers/auth.py`
- Inject `AuditService`.
- Emit `LOGIN` (success/failure) and `LOGOUT` events.

#### [MODIFY] `backend/app/routers/vulnerabilities.py`
- Emit `CREATE_FINDING`, `UPDATE_FINDING`, `STATUS_CHANGED` events.

#### [MODIFY] `backend/app/routers/integrations.py` & `backend/app/routers/tickets.py`
- Emit `TICKET_CREATED`, `TICKET_SYNCED`, `INTEGRATION_CONNECTED` events.

#### [MODIFY] `backend/app/routers/ci.py`
- Emit `GATE_EXECUTED` events.

#### [MODIFY] `backend/app/main.py`
- Register `audit.router`.

---

### Frontend

#### [NEW] `frontend/src/pages/Auditoria.tsx`
- Paginated table showing Data, Usuário, Ação, Entidade, ID, IP.
- Row expansion or Modal for detailed view (`Old Value`, `New Value`, `Metadata`), with sensitive data correctly rendered (and already masked by the backend).

#### [MODIFY] `frontend/src/App.tsx` & `frontend/src/components/Layout.tsx`
- Add routing and Sidebar entry for "Trilha de Auditoria", conditionally rendered if `user.roles` includes `AUDITOR`, `ADMIN`, `APPSEC`.

---

### Documentation & Tests

#### [NEW] `SDD/15-audit-log.md`
- Specify Acceptance Criteria (AC-AUDIT-01 to AC-AUDIT-xx).

#### [NEW] `backend/tests/test_audit.py`
- Test pagination, sanitization (passwords not leaked), RBAC constraints, and immutability (lack of PUT/DELETE endpoints).

#### [NEW] `frontend/src/pages/__tests__/Auditoria.test.tsx`
- Component testing.

#### [MODIFY] `ROADMAP_IMPLEMENTACAO.md`
- Mark Audit Log as implemented.

## Verification Plan

### Automated Tests
- Run `python -m pytest` focusing on the new `test_audit.py`.
- Run `vitest` to ensure frontend conditionally renders the menu.
- Run `scripts/rastreabilidade.py` to ensure all `AC-AUDIT` tags are fulfilled.

### Manual Verification
- Log in and verify that the `LOGIN` action is persisted.
- Perform a critical action (e.g. modify a ticket).
- Navigate to the new `/audit` page and verify it correctly exposes the previous and new values, properly masking any sensitive credentials.
