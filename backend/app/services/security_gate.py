# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
security_gate.py — Orquestra a avaliação de um pipeline pelo Security Gate.

Este serviço coordena:
1. Registrar/reencontrar o PipelineRun (idempotência via pipeline_id+commit_sha).
2. Invocar o Policy Engine para a aplicação.
3. Persistir o SecurityGateResult (histórico de decisões).
4. Notificar o provider de CI/CD (quando configurado).

A decisão (PASS/WARN/BLOCK) é sempre calculada localmente — o pipeline não
pode enviar a decisão já pronta e ter ela aceita.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TypedDict

from sqlalchemy.orm import Session

from app.models.ci import PipelineRun, SecurityGateResult
from app.models.enums import Ambiente, GateDecision
from app.services.policy_engine import ResultadoAvaliacao, ViolacaoPolicy, avaliar


class ViolacaoDict(TypedDict):
    policy_id: int
    policy_nome: str
    acao: str
    vulnerabilidade_id: int
    vulnerabilidade_tipo: str
    risco: str


@dataclass
class CheckRequest:
    """Dados enviados pelo pipeline ao acionar o Security Gate."""

    aplicacao_id: int
    commit_sha: str | None = None
    branch: str | None = None
    environment: str | None = None
    pipeline_id: str | None = None
    run_id: str | None = None
    provider: str | None = None


@dataclass
class CheckResponse:
    """Resposta do Security Gate para o pipeline."""

    decision: str  # "pass" | "warn" | "block"
    decision_label: str  # "Aprovado" | "Com aviso" | "Bloqueado"
    reason: str
    policy_violations: list[ViolacaoDict]
    findings: list[int]
    total_findings: int
    total_violations: int
    gate_result_id: int
    pipeline_run_id: int


def _serializar_violacoes(violations: list[ViolacaoPolicy]) -> str:
    """Serializa as violações para armazenamento em texto."""
    return json.dumps(
        [
            {
                "policy_id": v.policy_id,
                "policy_nome": v.policy_nome,
                "acao": v.acao.value,
                "vulnerabilidade_id": v.vulnerabilidade_id,
                "vulnerabilidade_tipo": v.vulnerabilidade_tipo,
                "risco": v.risco.value,
            }
            for v in violations
        ],
        ensure_ascii=False,
    )


def _violacoes_para_dict(violations: list[ViolacaoPolicy]) -> list[ViolacaoDict]:
    return [
        ViolacaoDict(
            policy_id=v.policy_id,
            policy_nome=v.policy_nome,
            acao=v.acao.value,
            vulnerabilidade_id=v.vulnerabilidade_id,
            vulnerabilidade_tipo=v.vulnerabilidade_tipo,
            risco=v.risco.value,
        )
        for v in violations
    ]


def _obter_ou_criar_pipeline_run(
    db: Session,
    req: CheckRequest,
) -> PipelineRun:
    """
    Idempotência: encontra o PipelineRun existente ou cria um novo.

    Critério de unicidade: (aplicacao_id, pipeline_id, commit_sha).
    Se ambos forem None, sempre cria um novo registro.
    """
    if req.pipeline_id or req.commit_sha:
        query = db.query(PipelineRun).filter(
            PipelineRun.aplicacao_id == req.aplicacao_id,
        )
        if req.pipeline_id:
            query = query.filter(PipelineRun.pipeline_id == req.pipeline_id)
        if req.commit_sha:
            query = query.filter(PipelineRun.commit_sha == req.commit_sha)
        existente = query.first()
        if existente:
            return existente

    ambiente: Ambiente | None = None
    if req.environment:
        try:
            ambiente = Ambiente(req.environment)
        except ValueError:
            pass  # ambiente desconhecido — mantém None

    run = PipelineRun(
        aplicacao_id=req.aplicacao_id,
        provider=req.provider,
        pipeline_id=req.pipeline_id,
        run_id=req.run_id,
        commit_sha=req.commit_sha,
        branch=req.branch,
        ambiente=ambiente,
    )
    db.add(run)
    db.flush()  # obtém o ID sem commitar ainda
    return run


def executar_check(
    db: Session,
    req: CheckRequest,
) -> CheckResponse:
    """
    Executa o Security Gate para um pipeline.

    1. Registra/encontra o PipelineRun.
    2. Avalia as políticas via policy_engine.
    3. Persiste o SecurityGateResult (sempre, mesmo em PASS — para histórico).
    4. Retorna a resposta estruturada.

    A decisão é sempre calculada aqui. O pipeline não pode influenciá-la.
    """
    run = _obter_ou_criar_pipeline_run(db, req)

    resultado: ResultadoAvaliacao = avaliar(req.aplicacao_id, db)

    # Persiste o resultado (histórico imutável — cada avaliação gera um novo registro)
    gate_result = SecurityGateResult(
        pipeline_run_id=run.id,
        decision=resultado.decision,
        reason=resultado.reason,
        policies_violated_json=_serializar_violacoes(resultado.violations),
        findings_json=json.dumps(resultado.findings_avaliados),
        total_findings=resultado.total_findings,
        total_violations=resultado.total_violations,
    )
    db.add(gate_result)
    db.commit()
    db.refresh(gate_result)
    db.refresh(run)

    decision_enum: GateDecision = resultado.decision
    return CheckResponse(
        decision=decision_enum.value,
        decision_label=decision_enum.label,
        reason=resultado.reason,
        policy_violations=_violacoes_para_dict(resultado.violations),
        findings=resultado.findings_avaliados,
        total_findings=resultado.total_findings,
        total_violations=resultado.total_violations,
        gate_result_id=gate_result.id,
        pipeline_run_id=run.id,
    )
