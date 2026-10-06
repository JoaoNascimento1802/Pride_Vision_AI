# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
policy_engine.py — Avalia as políticas ativas contra as vulnerabilidades abertas.

IMPORTANTE: Este módulo é determinístico — mesma entrada, mesma saída.
Nenhuma chamada de IA aqui. A IA pode *explicar* uma decisão, mas nunca a toma.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.enums import GateDecision, Risco, StatusVulnerabilidade
from app.models.policy import Policy, PolicyException
from app.models.vulnerability import Vulnerability

# Ordem de severidade para comparação de níveis de risco
_ORDEM_RISCO: dict[str, int] = {
    Risco.CRITICO.value: 0,
    Risco.ALTO.value: 1,
    Risco.MEDIO.value: 2,
    Risco.BAIXO.value: 3,
}

# Hierarquia de decisões: BLOCK > WARN > PASS
_ORDEM_DECISAO: dict[str, int] = {
    GateDecision.BLOCK.value: 0,
    GateDecision.WARN.value: 1,
    GateDecision.PASS.value: 2,
}


@dataclass
class ViolacaoPolicy:
    """Uma violação específica de uma política."""

    policy_id: int
    policy_nome: str
    acao: GateDecision
    vulnerabilidade_id: int
    vulnerabilidade_tipo: str
    risco: Risco


@dataclass
class ResultadoAvaliacao:
    """Resultado completo da avaliação das políticas."""

    decision: GateDecision
    reason: str
    violations: list[ViolacaoPolicy] = field(default_factory=list)
    findings_avaliados: list[int] = field(default_factory=list)  # IDs das vulnerabilidades

    @property
    def total_violations(self) -> int:
        return len(self.violations)

    @property
    def total_findings(self) -> int:
        return len(self.findings_avaliados)


def _risco_atinge_minimo(risco_vuln: Risco, risco_minimo: Risco) -> bool:
    """True se a vulnerabilidade tem risco igual ou mais grave que o mínimo da política."""
    return _ORDEM_RISCO[risco_vuln.value] <= _ORDEM_RISCO[risco_minimo.value]


def _tem_excecao_valida(
    vulnerabilidade: Vulnerability,
    policy: Policy,
    db: Session,
) -> bool:
    """
    Verifica se existe uma exceção válida (não expirada) para esta
    vulnerabilidade e política específicas.
    """
    excecoes: list[PolicyException] = (
        db.query(PolicyException)
        .filter(
            PolicyException.vulnerabilidade_id == vulnerabilidade.id,
            PolicyException.policy_id == policy.id,
        )
        .all()
    )
    return any(e.valida for e in excecoes)


def avaliar(
    aplicacao_id: int,
    db: Session,
    policies_extras: list[Policy] | None = None,
) -> ResultadoAvaliacao:
    """
    Avalia as políticas ativas para uma aplicação e retorna a decisão consolidada.

    Algoritmo:
    1. Carrega as políticas ativas: globais + específicas da aplicação.
    2. Carrega as vulnerabilidades abertas da aplicação.
    3. Para cada combinação (política, vulnerabilidade):
       - Se o risco da vuln atinge o mínimo da política → verifica exceção.
       - Sem exceção válida → registra violação com a ação da política.
    4. A decisão final é a ação mais restritiva entre todas as violações
       (BLOCK > WARN > PASS).

    Args:
        aplicacao_id: ID da aplicação a avaliar.
        db: Sessão do banco de dados.
        policies_extras: Políticas adicionais a considerar (para testes).

    Returns:
        ResultadoAvaliacao com a decisão e detalhes das violações.
    """
    # Carrega políticas ativas (globais + da aplicação)
    policies: list[Policy] = (
        db.query(Policy)
        .filter(
            Policy.ativa.is_(True),
            (Policy.aplicacao_id.is_(None)) | (Policy.aplicacao_id == aplicacao_id),
        )
        .all()
    )
    if policies_extras:
        policies = list(policies) + list(policies_extras)

    # Vulnerabilidades abertas (não corrigidas / não fechadas)
    status_abertos = [
        StatusVulnerabilidade.NOVA,
        StatusVulnerabilidade.EM_ANALISE,
        StatusVulnerabilidade.EM_CORRECAO,
    ]
    vulns: list[Vulnerability] = (
        db.query(Vulnerability)
        .filter(
            Vulnerability.aplicacao_id == aplicacao_id,
            Vulnerability.status.in_([s.value for s in status_abertos]),
        )
        .all()
    )

    ids_avaliados = [v.id for v in vulns]
    violations: list[ViolacaoPolicy] = []

    for policy in policies:
        for vuln in vulns:
            if not _risco_atinge_minimo(vuln.risco, policy.risco_minimo):
                continue
            # Risco atinge o mínimo → verifica se há exceção válida
            if _tem_excecao_valida(vuln, policy, db):
                continue
            # Sem exceção → violação registrada
            violations.append(
                ViolacaoPolicy(
                    policy_id=policy.id,
                    policy_nome=policy.nome,
                    acao=policy.acao,
                    vulnerabilidade_id=vuln.id,
                    vulnerabilidade_tipo=vuln.tipo_vuln,
                    risco=vuln.risco,
                )
            )

    # Determina a decisão mais restritiva
    if not violations:
        return ResultadoAvaliacao(
            decision=GateDecision.PASS,
            reason="Nenhuma violação de política detectada.",
            violations=[],
            findings_avaliados=ids_avaliados,
        )

    # A ação mais restritiva entre as violações
    decisao_final = min(
        violations,
        key=lambda v: _ORDEM_DECISAO[v.acao.value],
    ).acao

    # Monta o resumo das violações para a mensagem
    n_block = sum(1 for v in violations if v.acao is GateDecision.BLOCK)
    n_warn = sum(1 for v in violations if v.acao is GateDecision.WARN)

    partes: list[str] = []
    if n_block:
        partes.append(f"{n_block} violação(ões) bloqueante(s)")
    if n_warn:
        partes.append(f"{n_warn} alerta(s) não bloqueante(s)")

    reason = f"{decisao_final.icone} {decisao_final.label}: {', '.join(partes)}."

    return ResultadoAvaliacao(
        decision=decisao_final,
        reason=reason,
        violations=violations,
        findings_avaliados=ids_avaliados,
    )
