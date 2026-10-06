# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
ci.py — Schemas Pydantic para CI/CD e Security Gates.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ─── Request ────────────────────────────────────────────────────────────────


class CiCheckRequest(BaseModel):
    """Payload enviado pelo pipeline ao acionar o Security Gate."""

    application_id: int = Field(..., description="ID da aplicação no PRIDE")
    commit_sha: str | None = Field(None, description="SHA do commit avaliado")
    branch: str | None = Field(None, description="Branch sendo avaliada")
    environment: str | None = Field(None, description="Ambiente alvo: producao, homologacao, teste")
    pipeline_id: str | None = Field(None, description="ID do pipeline no provider")
    run_id: str | None = Field(None, description="ID da execução do pipeline")
    provider: str | None = Field(None, description="Provider de CI/CD: github, gitlab…")
    repository: str | None = Field(None, description="Repositório, ex: owner/repo")
    pull_request_number: int | None = Field(None, description="Número do PR/MR, se houver")


class PolicyExceptionRequest(BaseModel):
    """Payload para criar uma exceção de política."""

    policy_id: int
    vulnerability_id: int
    justificativa: str = Field(..., min_length=10)
    expira_em: datetime | None = Field(None, description="Data de expiração (None = permanente)")


# ─── Response ────────────────────────────────────────────────────────────────


class PolicyViolationResponse(BaseModel):
    policy_id: int
    policy_nome: str
    acao: str
    vulnerabilidade_id: int
    vulnerabilidade_tipo: str
    risco: str


class CiCheckResponse(BaseModel):
    """Resposta do Security Gate para o pipeline."""

    decision: str
    decision_label: str
    reason: str
    policy_violations: list[PolicyViolationResponse]
    findings: list[int]
    total_findings: int
    total_violations: int
    gate_result_id: int
    pipeline_run_id: int


class PolicyResponse(BaseModel):
    """Detalhes de uma política de segurança."""

    id: int
    aplicacao_id: int | None
    nome: str
    descricao: str | None
    risco_minimo: str
    acao: str
    ativa: bool
    criada_em: datetime

    model_config = {"from_attributes": True}


class PolicyCreateRequest(BaseModel):
    """Payload para criar uma política."""

    nome: str = Field(..., min_length=3, max_length=200)
    descricao: str | None = None
    aplicacao_id: int | None = None
    risco_minimo: str = Field("critico", description="critico, alto, medio, baixo")
    acao: str = Field("block", description="block, warn, pass")


class PolicyExceptionResponse(BaseModel):
    """Detalhes de uma exceção de política."""

    id: int
    policy_id: int
    vulnerabilidade_id: int
    justificativa: str
    expira_em: datetime | None
    valida: bool
    criada_em: datetime

    model_config = {"from_attributes": True}


class GateResultResponse(BaseModel):
    """Resultado histórico de um Security Gate."""

    id: int
    pipeline_run_id: int
    decision: str
    reason: str
    total_findings: int
    total_violations: int
    avaliado_em: datetime

    model_config = {"from_attributes": True}


class PipelineRunResponse(BaseModel):
    """Dados de uma execução de pipeline."""

    id: int
    aplicacao_id: int
    provider: str | None
    pipeline_id: str | None
    commit_sha: str | None
    branch: str | None
    ambiente: str | None
    criado_em: datetime
    ultimo_resultado: GateResultResponse | None

    model_config = {"from_attributes": True}
