# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
ci.py — Endpoints de CI/CD e Security Gates.

POST /api/ci/check          — Aciona o Security Gate para um pipeline.
GET  /api/ci/gate-results   — Histórico de resultados do gate (por aplicação).
GET  /api/ci/pipelines      — Pipelines registrados (por aplicação).
POST /api/ci/policies       — Cria uma política de segurança.
GET  /api/ci/policies       — Lista políticas ativas.
POST /api/ci/exceptions     — Cria exceção de política para uma vulnerabilidade.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.database import get_db
from app.models.ci import PipelineRun, SecurityGateResult
from app.models.enums import AuditAction, EntityType, GateDecision, Risco
from app.models.policy import Policy, PolicyException
from app.models.vulnerability import Vulnerability
from app.schemas.ci import (
    CiCheckRequest,
    CiCheckResponse,
    GateResultResponse,
    PipelineRunResponse,
    PolicyCreateRequest,
    PolicyExceptionRequest,
    PolicyExceptionResponse,
    PolicyResponse,
    PolicyViolationResponse,
)
from app.services.audit import AuditService, get_audit_service
from app.services.security_gate import CheckRequest, CheckResponse, executar_check

router = APIRouter(
    prefix="/api/ci",
    tags=["CI/CD Security Gates"],
    dependencies=[Depends(usuario_atual)],
)


# ─── Security Gate ────────────────────────────────────────────────────────────


@router.post("/check", response_model=CiCheckResponse, status_code=status.HTTP_200_OK)
def check_pipeline(
    req: CiCheckRequest,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("gate:check")),
    audit: AuditService = Depends(get_audit_service),
) -> Any:
    """
    Aciona o Security Gate para um pipeline.

    A decisão (PASS/WARN/BLOCK) é calculada pelo PRIDE com base nas
    vulnerabilidades abertas e nas políticas ativas. O pipeline não
    pode enviar a decisão pronta — ela é sempre computada aqui.

    Idempotente: a mesma combinação (aplicacao_id, pipeline_id, commit_sha)
    reencontra o PipelineRun existente e adiciona um novo SecurityGateResult.
    """
    check_req = CheckRequest(
        aplicacao_id=req.application_id,
        commit_sha=req.commit_sha,
        branch=req.branch,
        environment=req.environment,
        pipeline_id=req.pipeline_id,
        run_id=req.run_id,
        provider=req.provider,
    )
    try:
        result: CheckResponse = executar_check(db, check_req)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar Security Gate: {exc}",
        ) from exc

    # Publica feedback no PR/MR se o provider for conhecido e houver repositório
    if req.provider and req.repository:
        from app.services.ci_providers import get_ci_provider

        provider_svc = get_ci_provider(req.provider)
        if provider_svc:
            resumo = f"Status: **{result.decision.upper()}**\n\n"
            resumo += f"**Motivo:** {result.reason}\n"
            resumo += f"**Total de findings:** {result.total_findings}\n"
            resumo += f"**Violações bloqueantes:** {result.total_violations}\n"

            try:
                if req.pull_request_number:
                    provider_svc.publish_pr_feedback(
                        repository=req.repository,
                        pr_number=req.pull_request_number,
                        decision=GateDecision(result.decision),
                        summary=resumo,
                    )

                if req.commit_sha:
                    provider_svc.publish_status(
                        repository=req.repository,
                        commit_sha=req.commit_sha,
                        decision=GateDecision(result.decision),
                        description=result.reason,
                    )
            except Exception as exc:
                # Loga o erro, mas não falha o response do gate
                print(f"[WARN] Falha ao publicar feedback no {req.provider}: {exc}")

    audit.log_action(
        action=AuditAction.GATE_EXECUTED,
        actor_user_id=None, # Service account or pipeline actor usually doesn't have an ID
        entity_type=EntityType.SECURITY_GATE,
        entity_id=req.commit_sha or req.run_id,
        new_value={"decision": result.decision, "reason": result.reason},
        metadata_info={"application_id": req.application_id, "pipeline_id": req.pipeline_id}
    )
    db.commit()

    return CiCheckResponse(
        decision=result.decision,
        decision_label=result.decision_label,
        reason=result.reason,
        policy_violations=[
            PolicyViolationResponse(
                policy_id=v["policy_id"],
                policy_nome=v["policy_nome"],
                acao=v["acao"],
                vulnerabilidade_id=v["vulnerabilidade_id"],
                vulnerabilidade_tipo=v["vulnerabilidade_tipo"],
                risco=v["risco"],
            )
            for v in result.policy_violations
        ],
        findings=result.findings,
        total_findings=result.total_findings,
        total_violations=result.total_violations,
        gate_result_id=result.gate_result_id,
        pipeline_run_id=result.pipeline_run_id,
    )


# ─── Histórico de resultados ──────────────────────────────────────────────────


@router.get("/gate-results", response_model=list[GateResultResponse])
def listar_gate_results(
    aplicacao_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("gate:read")),
) -> Any:
    """Lista os resultados históricos do Security Gate, opcionalmente filtrados por aplicação."""
    query = db.query(SecurityGateResult).join(PipelineRun)
    if aplicacao_id:
        query = query.filter(PipelineRun.aplicacao_id == aplicacao_id)
    return query.order_by(SecurityGateResult.avaliado_em.desc()).limit(limit).all()


@router.get("/pipelines", response_model=list[PipelineRunResponse])
def listar_pipelines(
    aplicacao_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("gate:read")),
) -> Any:
    """Lista os pipelines registrados, com o último resultado de gate."""
    query = db.query(PipelineRun)
    if aplicacao_id:
        query = query.filter(PipelineRun.aplicacao_id == aplicacao_id)
    runs = query.order_by(PipelineRun.criado_em.desc()).limit(limit).all()

    responses = []
    for run in runs:
        ultimo = (
            db.query(SecurityGateResult)
            .filter(SecurityGateResult.pipeline_run_id == run.id)
            .order_by(SecurityGateResult.avaliado_em.desc())
            .first()
        )
        responses.append(
            PipelineRunResponse(
                id=run.id,
                aplicacao_id=run.aplicacao_id,
                provider=run.provider,
                pipeline_id=run.pipeline_id,
                commit_sha=run.commit_sha,
                branch=run.branch,
                ambiente=run.ambiente.value if run.ambiente else None,
                criado_em=run.criado_em,
                ultimo_resultado=(
                    GateResultResponse(
                        id=ultimo.id,
                        pipeline_run_id=ultimo.pipeline_run_id,
                        decision=ultimo.decision.value,
                        reason=ultimo.reason,
                        total_findings=ultimo.total_findings,
                        total_violations=ultimo.total_violations,
                        avaliado_em=ultimo.avaliado_em,
                    )
                    if ultimo
                    else None
                ),
            )
        )
    return responses


# ─── Políticas ────────────────────────────────────────────────────────────────


@router.post("/policies", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def criar_policy(
    req: PolicyCreateRequest,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("policy:write")),
    audit: AuditService = Depends(get_audit_service),
) -> Any:
    """Cria uma nova política de segurança."""
    try:
        risco = Risco(req.risco_minimo)
        acao = GateDecision(req.acao)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    policy = Policy(
        nome=req.nome,
        descricao=req.descricao,
        aplicacao_id=req.aplicacao_id,
        risco_minimo=risco,
        acao=acao,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    audit.log_action(
        action=AuditAction.CREATE_POLICY,
        actor_user_id=_usuario.id if hasattr(_usuario, "id") else None,
        entity_type=EntityType.POLICY,
        entity_id=str(policy.id),
        new_value={"nome": policy.nome, "risco_minimo": policy.risco_minimo.value, "acao": policy.acao.value}
    )
    db.commit()
    return policy


@router.get("/policies", response_model=list[PolicyResponse])
def listar_policies(
    aplicacao_id: int | None = None,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("policy:read")),
) -> Any:
    """Lista políticas ativas, opcionalmente filtradas por aplicação."""
    query = db.query(Policy).filter(Policy.ativa.is_(True))
    if aplicacao_id is not None:
        query = query.filter(
            (Policy.aplicacao_id.is_(None)) | (Policy.aplicacao_id == aplicacao_id)
        )
    return query.order_by(Policy.id).all()


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("policy:write")),
    audit: AuditService = Depends(get_audit_service),
) -> None:
    """Desativa uma política (soft delete)."""
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Política não encontrada."
        )
    policy.ativa = False
    audit.log_action(
        action=AuditAction.DELETE_POLICY,
        actor_user_id=_usuario.id if hasattr(_usuario, "id") else None,
        entity_type=EntityType.POLICY,
        entity_id=str(policy.id),
        old_value={"ativa": True},
        new_value={"ativa": False}
    )
    db.commit()


# ─── Exceções ─────────────────────────────────────────────────────────────────


@router.post(
    "/exceptions", response_model=PolicyExceptionResponse, status_code=status.HTTP_201_CREATED
)
def criar_excecao(
    req: PolicyExceptionRequest,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("exception:write")),
    audit: AuditService = Depends(get_audit_service),
) -> Any:
    """
    Cria uma exceção para uma vulnerabilidade em uma política específica.

    A exceção permite que o Security Gate não bloqueie por aquela combinação
    (policy, vulnerabilidade) enquanto a exceção for válida.
    """
    policy = db.get(Policy, req.policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Política não encontrada."
        )

    vuln = db.get(Vulnerability, req.vulnerability_id)
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerabilidade não encontrada."
        )

    excecao = PolicyException(
        policy_id=req.policy_id,
        vulnerabilidade_id=req.vulnerability_id,
        justificativa=req.justificativa,
        expira_em=req.expira_em,
        aprovado_por_id=usuario.id,
    )
    db.add(excecao)
    db.commit()
    db.refresh(excecao)

    audit.log_action(
        action=AuditAction.CREATE_EXCEPTION,
        actor_user_id=usuario.id if hasattr(usuario, "id") else None,
        entity_type=EntityType.EXCEPTION,
        entity_id=str(excecao.id),
        new_value={"policy_id": req.policy_id, "vulnerability_id": req.vulnerability_id, "justificativa": req.justificativa, "expira_em": req.expira_em.isoformat() if req.expira_em else None}
    )
    db.commit()

    return PolicyExceptionResponse(
        id=excecao.id,
        policy_id=excecao.policy_id,
        vulnerabilidade_id=excecao.vulnerabilidade_id,
        justificativa=excecao.justificativa,
        expira_em=excecao.expira_em,
        valida=excecao.valida,
        criada_em=excecao.criada_em,
    )


@router.get("/exceptions", response_model=list[PolicyExceptionResponse])
def listar_excecoes(
    vulnerability_id: int | None = None,
    db: Session = Depends(get_db),
    _usuario: Any = Depends(RequirePermission("exception:read")),
) -> Any:
    """Lista exceções de política, opcionalmente filtradas por vulnerabilidade."""
    query = db.query(PolicyException)
    if vulnerability_id:
        query = query.filter(PolicyException.vulnerabilidade_id == vulnerability_id)
    excecoes = query.order_by(PolicyException.id.desc()).all()
    return [
        PolicyExceptionResponse(
            id=e.id,
            policy_id=e.policy_id,
            vulnerabilidade_id=e.vulnerabilidade_id,
            justificativa=e.justificativa,
            expira_em=e.expira_em,
            valida=e.valida,
            criada_em=e.criada_em,
        )
        for e in excecoes
    ]
