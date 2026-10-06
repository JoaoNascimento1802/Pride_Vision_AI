# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
test_security_gate.py — Testes unitários do Policy Engine e Security Gate.

Valida os cenários PASS, WARN, BLOCK, com e sem exceções, expiradas ou não.
Referência: AC-CI-05 a AC-CI-15.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.enums import (
    Ambiente,
    Exposicao,
    GateDecision,
    Importancia,
    Risco,
    StatusVulnerabilidade,
)
from app.models.policy import Policy, PolicyException
from app.models.vulnerability import Vulnerability
from app.services.policy_engine import avaliar


@pytest.fixture
def app_db(db: Session) -> dict:
    """Cria uma aplicação de produção diretamente no banco (sem HTTP)."""
    app_obj = Application(
        nome="API de Teste",
        responsavel="Time AppSec",
        ambiente=Ambiente.PRODUCAO,
        exposicao=Exposicao.INTERNET,
        importancia=Importancia.ALTA,
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return {"id": app_obj.id}


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _criar_vuln(
    db: Session,
    aplicacao_id: int,
    risco: Risco = Risco.CRITICO,
    status: StatusVulnerabilidade = StatusVulnerabilidade.NOVA,
) -> Vulnerability:
    vuln = Vulnerability(
        aplicacao_id=aplicacao_id,
        tipo_vuln="sql_injection",
        endpoint="/api/login",
        risco=risco,
        justificativa="Teste",
        correlacionada=True,
        encontrada_semgrep=True,
        status=status,
    )
    db.add(vuln)
    db.flush()
    return vuln


def _criar_policy_block(
    db: Session,
    risco_minimo: Risco = Risco.CRITICO,
    aplicacao_id: int | None = None,
) -> Policy:
    policy = Policy(
        nome="Bloquear crítico",
        risco_minimo=risco_minimo,
        acao=GateDecision.BLOCK,
        aplicacao_id=aplicacao_id,
    )
    db.add(policy)
    db.flush()
    return policy


def _criar_policy_warn(db: Session) -> Policy:
    policy = Policy(
        nome="Alertar alto",
        risco_minimo=Risco.ALTO,
        acao=GateDecision.WARN,
    )
    db.add(policy)
    db.flush()
    return policy


def _criar_excecao(
    db: Session,
    policy: Policy,
    vuln: Vulnerability,
    expira_em: datetime | None = None,
) -> PolicyException:
    exc = PolicyException(
        policy_id=policy.id,
        vulnerabilidade_id=vuln.id,
        justificativa="Aceito temporariamente enquanto correção está em andamento.",
        expira_em=expira_em,
    )
    db.add(exc)
    db.flush()
    return exc


# ─── AC-CI-05 ────────────────────────────────────────────────────────────────


def test_gate_pass_sem_vulnerabilidades(db: Session, app_db: dict) -> None:
    """AC-CI-05 — Sem vulnerabilidades abertas → PASS."""
    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS
    assert resultado.total_violations == 0


# ─── AC-CI-05 (sem políticas) ────────────────────────────────────────────────


def test_gate_pass_sem_policies(db: Session, app_db: dict) -> None:
    """AC-CI-05 — Com vulnerabilidade mas sem políticas ativas → PASS."""
    _criar_vuln(db, app_db["id"])
    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS


# ─── AC-CI-06 ────────────────────────────────────────────────────────────────


def test_gate_block_critico_sem_excecao(db: Session, app_db: dict) -> None:
    """AC-CI-06 — Vulnerabilidade crítica + política BLOCK → BLOCK."""
    _criar_vuln(db, app_db["id"], risco=Risco.CRITICO)
    _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.BLOCK
    assert resultado.total_violations == 1


# ─── AC-CI-07 ────────────────────────────────────────────────────────────────


def test_gate_pass_com_excecao_valida(db: Session, app_db: dict) -> None:
    """AC-CI-07 — Vulnerabilidade crítica + exceção válida → PASS."""
    vuln = _criar_vuln(db, app_db["id"], risco=Risco.CRITICO)
    policy = _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    # Exceção válida por mais 30 dias
    expira = datetime.now(UTC) + timedelta(days=30)
    _criar_excecao(db, policy, vuln, expira_em=expira)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS
    assert resultado.total_violations == 0


# ─── AC-CI-08 ────────────────────────────────────────────────────────────────


def test_gate_block_com_excecao_expirada(db: Session, app_db: dict) -> None:
    """AC-CI-08 — Exceção expirada → a política volta a bloquear."""
    vuln = _criar_vuln(db, app_db["id"], risco=Risco.CRITICO)
    policy = _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    # Exceção já expirada
    expirada = datetime.now(UTC) - timedelta(days=1)
    _criar_excecao(db, policy, vuln, expira_em=expirada)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.BLOCK


# ─── AC-CI-09 ────────────────────────────────────────────────────────────────


def test_gate_warn_policy_warn(db: Session, app_db: dict) -> None:
    """AC-CI-09 — Política WARN sem exceção → WARN."""
    _criar_vuln(db, app_db["id"], risco=Risco.ALTO)
    _criar_policy_warn(db)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.WARN


# ─── AC-CI-10 ────────────────────────────────────────────────────────────────


def test_gate_block_prevalece_sobre_warn(db: Session, app_db: dict) -> None:
    """AC-CI-10 — BLOCK + WARN → BLOCK (mais restritivo prevalece)."""
    _criar_vuln(db, app_db["id"], risco=Risco.CRITICO)
    _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    _criar_policy_warn(db)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.BLOCK


# ─── AC-CI-14 ────────────────────────────────────────────────────────────────


def test_excecao_permanente_valida(db: Session, app_db: dict) -> None:
    """AC-CI-14 — Exceção sem data de expiração é sempre válida."""
    vuln = _criar_vuln(db, app_db["id"], risco=Risco.CRITICO)
    policy = _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    _criar_excecao(db, policy, vuln, expira_em=None)  # permanente
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS


# ─── Vulnerabilidade fechada não entra na avaliação ──────────────────────────


def test_gate_ignora_vuln_corrigida(db: Session, app_db: dict) -> None:
    """Vulnerabilidade com status CORRIGIDA não deve entrar na avaliação do gate."""
    _criar_vuln(
        db,
        app_db["id"],
        risco=Risco.CRITICO,
        status=StatusVulnerabilidade.CORRIGIDA,
    )
    _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS


def test_gate_ignora_vuln_falso_positivo(db: Session, app_db: dict) -> None:
    """Vulnerabilidade com status FALSO_POSITIVO não bloqueia o gate."""
    _criar_vuln(
        db,
        app_db["id"],
        risco=Risco.CRITICO,
        status=StatusVulnerabilidade.FALSO_POSITIVO,
    )
    _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS


# ─── Risco abaixo do mínimo não dispara a política ───────────────────────────


def test_gate_risco_baixo_nao_aciona_policy_critico(db: Session, app_db: dict) -> None:
    """Política que exige risco CRITICO não é acionada por vuln de risco BAIXO."""
    _criar_vuln(db, app_db["id"], risco=Risco.BAIXO)
    _criar_policy_block(db, risco_minimo=Risco.CRITICO)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS


# ─── Policy específica por aplicação ─────────────────────────────────────────


def test_policy_especifica_nao_aplica_outra_aplicacao(
    db: Session,
    app_db: dict,
) -> None:
    """Política específica para outra app não afeta a aplicação do teste."""
    from app.models.application import Application
    from app.models.enums import Ambiente, Exposicao, Importancia

    # Cria uma segunda aplicação real
    outra_app = Application(
        nome="Outra Aplicação",
        responsavel="Time X",
        ambiente=Ambiente.TESTE,
        exposicao=Exposicao.INTERNA,
        importancia=Importancia.BAIXA,
    )
    db.add(outra_app)
    db.flush()

    _criar_vuln(db, app_db["id"], risco=Risco.CRITICO)
    # policy específica para outra_app — NÃO deve se aplicar a app_db
    policy = Policy(
        nome="Bloquear críticos — outra app",
        risco_minimo=Risco.CRITICO,
        acao=GateDecision.BLOCK,
        aplicacao_id=outra_app.id,
    )
    db.add(policy)
    db.commit()

    resultado = avaliar(app_db["id"], db)
    assert resultado.decision is GateDecision.PASS
