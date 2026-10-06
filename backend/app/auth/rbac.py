# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from enum import StrEnum

from app.models.enums import Role


class Permission(StrEnum):
    # Aplicações
    APPLICATION_READ = "application:read"
    APPLICATION_WRITE = "application:write"

    # Findings
    FINDING_READ = "finding:read"
    FINDING_WRITE = "finding:write"
    FINDING_CLOSE = "finding:close"

    # Ticket
    TICKET_READ = "ticket:read"
    TICKET_CREATE = "ticket:create"
    TICKET_SYNC = "ticket:sync"

    # Uploads (SCA/DAST/etc)
    UPLOAD_CREATE = "upload:create"

    # Admin
    USER_MANAGE = "user:manage"
    AUDIT_READ = "audit:read"

    # CI/CD Security Gates
    GATE_READ = "gate:read"
    GATE_CHECK = "gate:check"
    POLICY_READ = "policy:read"
    POLICY_WRITE = "policy:write"
    EXCEPTION_READ = "exception:read"
    EXCEPTION_WRITE = "exception:write"
    API_SECURITY_READ = "api_security:read"
    API_SECURITY_WRITE = "api_security:write"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.APPLICATION_READ,
        Permission.APPLICATION_WRITE,
        Permission.FINDING_READ,
        Permission.FINDING_WRITE,
        Permission.FINDING_CLOSE,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_SYNC,
        Permission.UPLOAD_CREATE,
        Permission.USER_MANAGE,
        Permission.AUDIT_READ,
        Permission.GATE_READ,
        Permission.GATE_CHECK,
        Permission.POLICY_READ,
        Permission.POLICY_WRITE,
        Permission.EXCEPTION_READ,
        Permission.EXCEPTION_WRITE,
        Permission.API_SECURITY_READ,
        Permission.API_SECURITY_WRITE,
    },
    Role.APPSEC: {
        Permission.APPLICATION_READ,
        Permission.APPLICATION_WRITE,
        Permission.FINDING_READ,
        Permission.FINDING_WRITE,
        Permission.FINDING_CLOSE,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_SYNC,
        Permission.UPLOAD_CREATE,
        Permission.AUDIT_READ,
        Permission.GATE_READ,
        Permission.GATE_CHECK,
        Permission.POLICY_READ,
        Permission.POLICY_WRITE,
        Permission.EXCEPTION_READ,
        Permission.EXCEPTION_WRITE,
        Permission.API_SECURITY_READ,
        Permission.API_SECURITY_WRITE,
    },
    Role.TECH_LEAD: {
        Permission.API_SECURITY_READ,
        Permission.APPLICATION_READ,
        Permission.FINDING_READ,
        Permission.FINDING_WRITE,
        Permission.FINDING_CLOSE,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_SYNC,
        Permission.UPLOAD_CREATE,
        Permission.GATE_READ,
        Permission.GATE_CHECK,
        Permission.POLICY_READ,
        Permission.EXCEPTION_READ,
        Permission.EXCEPTION_WRITE,
        Permission.API_SECURITY_READ,
        Permission.API_SECURITY_WRITE,
    },
    Role.DEVELOPER: {
        Permission.API_SECURITY_READ,
        Permission.APPLICATION_READ,
        Permission.FINDING_READ,
        Permission.TICKET_READ,
        Permission.TICKET_CREATE,
        Permission.TICKET_SYNC,
        Permission.GATE_READ,
        Permission.EXCEPTION_READ,
    },
    Role.MANAGER: {
        Permission.APPLICATION_READ,
        Permission.FINDING_READ,
        Permission.AUDIT_READ,
        Permission.GATE_READ,
        Permission.POLICY_READ,
        Permission.EXCEPTION_READ,
    },
    Role.AUDITOR: {
        Permission.APPLICATION_READ,
        Permission.FINDING_READ,
        Permission.AUDIT_READ,
        Permission.GATE_READ,
        Permission.POLICY_READ,
        Permission.EXCEPTION_READ,
    },
}


def get_permissions(role: Role) -> list[str]:
    return [p.value for p in ROLE_PERMISSIONS.get(role, set())]
