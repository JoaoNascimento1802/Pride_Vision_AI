# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
models â€” Modelos ORM da plataforma.

Importar este pacote registra todas as tabelas no metadata da Base, que Ã© o que
`criar_tabelas()` precisa para saber o que criar.
"""

from app.models.api_asset import ApiAsset, ApiEndpoint
from app.models.application import Application
from app.models.audit import AuditLog
from app.models.ci import PipelineRun, SecurityGateResult
from app.models.cloud import CloudAccount, CloudResource
from app.models.container import ContainerImage, ContainerInstance
from app.models.enums import (
    Ambiente,
    Exposicao,
    Ferramenta,
    GateDecision,
    Importancia,
    Risco,
    Role,
    StatusVulnerabilidade,
    TicketProvider,
    TicketStatus,
)
from app.models.ingestion import Finding, Upload
from app.models.integration import Integration
from app.models.policy import Policy, PolicyException
from app.models.remediation import RemediationComment, RemediationEvidence
from app.models.sbom import Sbom, SbomComponent
from app.models.supply_chain import ArtifactVerification
from app.models.tenant import Tenant, TenantUser
from app.models.ticket import Ticket
from app.models.user import User
from app.models.vulnerability import StatusHistory, Vulnerability

__all__ = [
    "Ambiente",
    "ApiAsset",
    "ApiEndpoint",
    "Application",
    "AuditLog",
    "ContainerImage",
    "Exposicao",
    "Ferramenta",
    "Finding",
    "Integration",
    "GateDecision",
    "Importancia",
    "PipelineRun",
    "Policy",
    "PolicyException",
    "RemediationComment",
    "RemediationEvidence",
    "Risco",
    "Role",
    "Sbom",
    "SbomComponent", "ArtifactVerification",
    "SecurityGateResult",
    "StatusHistory",
    "StatusVulnerabilidade",
    "Ticket",
    "TicketProvider",
    "TicketStatus",
    "Upload",
    "User",
    "Tenant",
    "TenantUser",
    "Vulnerability",
    "ContainerInstance",
    "CloudAccount",
    "CloudResource",
]
