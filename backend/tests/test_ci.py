# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
test_ci.py — Testes de integração dos endpoints de CI/CD e Security Gates.

Referência: AC-CI-01 a AC-CI-20.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import GateDecision, Risco, StatusVulnerabilidade
from app.models.vulnerability import Vulnerability

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _inserir_vuln_critica(db: Session, aplicacao_id: int) -> Vulnerability:
    vuln = Vulnerability(
        aplicacao_id=aplicacao_id,
        tipo_vuln="rce",
        endpoint="/api/exec",
        risco=Risco.CRITICO,
        justificativa="Execução remota de código",
        correlacionada=True,
        encontrada_semgrep=True,
        status=StatusVulnerabilidade.NOVA,
    )
    db.add(vuln)
    db.commit()
    db.refresh(vuln)
    return vuln


def _criar_policy_via_api(
    client: TestClient,
    auth: dict[str, str],
    risco_minimo: str = "critico",
    acao: str = "block",
) -> dict:
    resp = client.post(
        "/api/ci/policies",
        headers=auth,
        json={
            "nome": "Bloquear críticos em produção",
            "risco_minimo": risco_minimo,
            "acao": acao,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _check_pipeline(
    client: TestClient,
    auth: dict[str, str],
    aplicacao_id: int,
    pipeline_id: str | None = "pipe-001",
    commit_sha: str | None = "abc123",
) -> dict:
    resp = client.post(
        "/api/ci/check",
        headers=auth,
        json={
            "application_id": aplicacao_id,
            "commit_sha": commit_sha,
            "branch": "main",
            "environment": "producao",
            "pipeline_id": pipeline_id,
            "provider": "github",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ─── AC-CI-01 ────────────────────────────────────────────────────────────────


def test_criar_policy(client: TestClient, auth: dict[str, str], aplicacao_producao: dict) -> None:
    """AC-CI-01 — Criar política retorna 201 com dados corretos."""
    resp = client.post(
        "/api/ci/policies",
        headers=auth,
        json={"nome": "Block crítico", "risco_minimo": "critico", "acao": "block"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == "Block crítico"
    assert data["ativa"] is True
    assert data["acao"] == "block"


# ─── AC-CI-02 ────────────────────────────────────────────────────────────────


def test_listar_policies(client: TestClient, auth: dict[str, str]) -> None:
    """AC-CI-02 — Listar políticas retorna lista de políticas ativas."""
    _criar_policy_via_api(client, auth)
    resp = client.get("/api/ci/policies", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ─── AC-CI-03 ────────────────────────────────────────────────────────────────


def test_desativar_policy(client: TestClient, auth: dict[str, str]) -> None:
    """AC-CI-03 — Desativar política retorna 204 e ela some da lista."""
    policy = _criar_policy_via_api(client, auth)
    pid = policy["id"]

    resp = client.delete(f"/api/ci/policies/{pid}", headers=auth)
    assert resp.status_code == 204

    lista = client.get("/api/ci/policies", headers=auth).json()
    assert not any(p["id"] == pid for p in lista)


# ─── AC-CI-04 ────────────────────────────────────────────────────────────────


def test_developer_nao_pode_criar_policy(
    client: TestClient,
    auth: dict[str, str],
    db: Session,
) -> None:
    """AC-CI-04 — DEVELOPER não pode criar política (403)."""
    from app.models.enums import Role
    from app.models.user import User

    # Rebaixa o usuário para DEVELOPER
    user = db.query(User).first()
    assert user is not None
    user.role = Role.DEVELOPER
    db.commit()

    resp = client.post(
        "/api/ci/policies",
        headers=auth,
        json={"nome": "X", "risco_minimo": "critico", "acao": "block"},
    )
    assert resp.status_code == 403


# ─── AC-CI-05 ────────────────────────────────────────────────────────────────


def test_check_pass_sem_vulnerabilidades(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict
) -> None:
    """AC-CI-05 — Sem vulnerabilidades e sem políticas → decision=pass."""
    result = _check_pipeline(client, auth, aplicacao_producao["id"])
    assert result["decision"] == GateDecision.PASS.value


# ─── AC-CI-06 ────────────────────────────────────────────────────────────────


def test_check_block_critico(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-06 — Vulnerabilidade crítica + política BLOCK → decision=block."""
    _inserir_vuln_critica(db, aplicacao_producao["id"])
    _criar_policy_via_api(client, auth, risco_minimo="critico", acao="block")

    result = _check_pipeline(client, auth, aplicacao_producao["id"])
    assert result["decision"] == GateDecision.BLOCK.value
    assert result["total_violations"] >= 1


# ─── AC-CI-07 ────────────────────────────────────────────────────────────────


def test_check_pass_com_excecao_valida(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-07 — Com exceção válida, decisão muda de BLOCK para PASS."""
    vuln = _inserir_vuln_critica(db, aplicacao_producao["id"])
    policy = _criar_policy_via_api(client, auth, risco_minimo="critico", acao="block")

    expira = datetime.now(UTC) + timedelta(days=30)
    resp = client.post(
        "/api/ci/exceptions",
        headers=auth,
        json={
            "policy_id": policy["id"],
            "vulnerability_id": vuln.id,
            "justificativa": "Correção em andamento, prazo acertado com o time.",
            "expira_em": expira.isoformat(),
        },
    )
    assert resp.status_code == 201
    assert resp.json()["valida"] is True

    result = _check_pipeline(client, auth, aplicacao_producao["id"], pipeline_id="pipe-007")
    assert result["decision"] == GateDecision.PASS.value


# ─── AC-CI-08 ────────────────────────────────────────────────────────────────


def test_check_block_excecao_expirada(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-08 — Exceção expirada → gate volta a bloquear."""
    vuln = _inserir_vuln_critica(db, aplicacao_producao["id"])
    policy = _criar_policy_via_api(client, auth, risco_minimo="critico", acao="block")

    expirada = datetime.now(UTC) - timedelta(days=1)
    client.post(
        "/api/ci/exceptions",
        headers=auth,
        json={
            "policy_id": policy["id"],
            "vulnerability_id": vuln.id,
            "justificativa": "Exceção expirada para teste.",
            "expira_em": expirada.isoformat(),
        },
    )

    result = _check_pipeline(client, auth, aplicacao_producao["id"], pipeline_id="pipe-008")
    assert result["decision"] == GateDecision.BLOCK.value


# ─── AC-CI-09 ────────────────────────────────────────────────────────────────


def test_check_warn(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-09 — Política WARN → decision=warn."""
    vuln = Vulnerability(
        aplicacao_id=aplicacao_producao["id"],
        tipo_vuln="xss",
        endpoint="/search",
        risco=Risco.ALTO,
        justificativa="XSS refletido",
        correlacionada=False,
        encontrada_semgrep=True,
        status=StatusVulnerabilidade.NOVA,
    )
    db.add(vuln)
    db.commit()

    _criar_policy_via_api(client, auth, risco_minimo="alto", acao="warn")

    result = _check_pipeline(client, auth, aplicacao_producao["id"], pipeline_id="pipe-009")
    assert result["decision"] == GateDecision.WARN.value


# ─── AC-CI-11 (idempotência) ─────────────────────────────────────────────────


def test_check_idempotencia_mesmo_pipeline(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-11 — Mesmo pipeline_id+commit_sha → mesmo PipelineRun, novo GateResult."""
    _check_pipeline(client, auth, aplicacao_producao["id"], pipeline_id="pipe-A", commit_sha="sha1")
    result2 = _check_pipeline(
        client, auth, aplicacao_producao["id"], pipeline_id="pipe-A", commit_sha="sha1"
    )

    # Ambas as chamadas retornam o mesmo pipeline_run_id
    result1 = _check_pipeline(
        client, auth, aplicacao_producao["id"], pipeline_id="pipe-A", commit_sha="sha1"
    )
    assert result1["pipeline_run_id"] == result2["pipeline_run_id"]

    # Mas gate_result_id é diferente (novo registro a cada avaliação)
    assert result1["gate_result_id"] != result2["gate_result_id"]


# ─── AC-CI-12 ────────────────────────────────────────────────────────────────


def test_check_sem_pipeline_id_cria_novo_run(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict
) -> None:
    """AC-CI-12 — Sem pipeline_id/commit_sha → cada chamada cria um PipelineRun novo."""
    resp1 = client.post(
        "/api/ci/check",
        headers=auth,
        json={"application_id": aplicacao_producao["id"]},
    )
    resp2 = client.post(
        "/api/ci/check",
        headers=auth,
        json={"application_id": aplicacao_producao["id"]},
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["pipeline_run_id"] != resp2.json()["pipeline_run_id"]


# ─── AC-CI-15 ────────────────────────────────────────────────────────────────


def test_developer_nao_pode_criar_excecao(
    client: TestClient, auth: dict[str, str], db: Session, aplicacao_producao: dict
) -> None:
    """AC-CI-15 — DEVELOPER não pode criar exceção (403)."""
    from app.models.enums import Role
    from app.models.user import User

    user = db.query(User).first()
    assert user is not None
    user.role = Role.DEVELOPER
    db.commit()

    resp = client.post(
        "/api/ci/exceptions",
        headers=auth,
        json={
            "policy_id": 1,
            "vulnerability_id": 1,
            "justificativa": "Tentativa de criar exceção como developer.",
        },
    )
    assert resp.status_code == 403


# ─── AC-CI-16 ────────────────────────────────────────────────────────────────


def test_listar_gate_results(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict
) -> None:
    """AC-CI-16 — Histórico de gate results acessível via GET."""
    _check_pipeline(
        client, auth, aplicacao_producao["id"], pipeline_id="pipe-16", commit_sha="sha-16"
    )

    resp = client.get(
        f"/api/ci/gate-results?aplicacao_id={aplicacao_producao['id']}",
        headers=auth,
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ─── AC-CI-17 ────────────────────────────────────────────────────────────────


def test_listar_pipelines_com_ultimo_resultado(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict
) -> None:
    """AC-CI-17 — Listar pipelines inclui ultimo_resultado."""
    _check_pipeline(
        client, auth, aplicacao_producao["id"], pipeline_id="pipe-17", commit_sha="sha-17"
    )

    resp = client.get(
        f"/api/ci/pipelines?aplicacao_id={aplicacao_producao['id']}",
        headers=auth,
    )
    assert resp.status_code == 200
    runs = resp.json()
    assert len(runs) >= 1
    assert runs[0]["ultimo_resultado"] is not None
    assert "decision" in runs[0]["ultimo_resultado"]


# ─── AC-CI-18 ────────────────────────────────────────────────────────────────


def test_decision_calculada_internamente(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-18 — O campo 'decision' no request é ignorado; PRIDE calcula internamente."""
    _inserir_vuln_critica(db, aplicacao_producao["id"])
    _criar_policy_via_api(client, auth, risco_minimo="critico", acao="block")

    # Envia decision=pass no payload — deve ser ignorado
    resp = client.post(
        "/api/ci/check",
        headers=auth,
        json={
            "application_id": aplicacao_producao["id"],
            "decision": "pass",  # campo inexistente no schema — ignorado pelo Pydantic
        },
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == GateDecision.BLOCK.value  # calculado corretamente


# ─── AC-CI-19 ────────────────────────────────────────────────────────────────


def test_check_sem_autenticacao(client: TestClient, aplicacao_producao: dict) -> None:
    """AC-CI-19 — Sem token → 401."""
    resp = client.post(
        "/api/ci/check",
        json={"application_id": aplicacao_producao["id"]},
    )
    assert resp.status_code == 401


# ─── AC-CI-20 ────────────────────────────────────────────────────────────────


def test_resposta_sem_segredos(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-20 — Resposta do gate não contém tokens, senhas ou segredos."""
    _inserir_vuln_critica(db, aplicacao_producao["id"])
    _criar_policy_via_api(client, auth, risco_minimo="critico", acao="block")

    result = _check_pipeline(client, auth, aplicacao_producao["id"], pipeline_id="pipe-20")
    resposta_str = str(result)

    # A resposta não deve conter padrões de segredo
    assert "Bearer " not in resposta_str
    assert "access_token" not in resposta_str
    assert "password" not in resposta_str
    assert "api_key" not in resposta_str


# ─── AC-CI-13 ────────────────────────────────────────────────────────────────


def test_criar_excecao_retorna_valida(
    client: TestClient, auth: dict[str, str], aplicacao_producao: dict, db: Session
) -> None:
    """AC-CI-13 — Exceção criada via POST /api/ci/exceptions é persistida com valida=True."""
    vuln = _inserir_vuln_critica(db, aplicacao_producao["id"])
    policy = _criar_policy_via_api(client, auth, risco_minimo="critico", acao="block")

    expira = (datetime.now(UTC) + timedelta(days=30)).isoformat()

    resp = client.post(
        "/api/ci/exceptions",
        headers=auth,
        json={
            "policy_id": policy["id"],
            "vulnerability_id": vuln.id,
            "justificativa": "Exceção criada para validação do AC-CI-13.",
            "expira_em": expira,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["valida"] is True
    assert data["policy_id"] == policy["id"]
    assert data["vulnerabilidade_id"] == vuln.id
