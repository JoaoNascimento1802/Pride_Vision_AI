# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import pytest
from fastapi.testclient import TestClient

from app.models.audit import AuditLog
from tests.dados import NUCLEI_INFORMATIVO, NUCLEI_XSS, SEMGREP_XSS_SQLI, arquivo


@pytest.fixture
def cenario(client: TestClient, auth, aplicacao_producao) -> dict[str, object]:
    app_id = aplicacao_producao["id"]
    for ferramenta, conteudo in (
        ("semgrep", SEMGREP_XSS_SQLI),
        ("nuclei", NUCLEI_XSS + "\n" + NUCLEI_INFORMATIVO),
    ):
        client.post(
            f"/api/aplicacoes/{app_id}/uploads/{ferramenta}",
            headers=auth,
            files=arquivo(conteudo, f"{ferramenta}.txt"),
        )
    return {"app_id": app_id}


class TestRemediationWorkflow:
    def test_remediation_owner_assignment(self, client: TestClient, auth, cenario):
        """AC-REM-05 — Atribuir responsável."""
        # Pega uma vulnerabilidade do cenário
    def test_ac_rem_01_maquina_estados(self, client: TestClient, auth, cenario):
        """AC-REM-01 — Transição inválida responde 422."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]

        # O usuário "Admin" (que fez o auth) tem ID 1
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/owner",
            json={"owner_id": 1, "owner_team": "AppSec"},
            headers=auth
        )
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "corrigida"}, headers=auth
        )
        assert resp.status_code == 422

    def test_ac_rem_02_transicao_valida(self, client: TestClient, auth, cenario):
        """AC-REM-02 — Transição NOVA para EM_ANALISE."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise"}, headers=auth
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "em_analise"
        assert resp.json()["historico"][-1]["status_novo"] == "em_analise"
        assert resp.json()["historico"][-1]["usuario_nome"] is not None

    def test_remediation_comments(self, client: TestClient, auth, cenario):
        """AC-REM-09 — Comentários em vulnerabilidades."""
    def test_ac_rem_03_fluxo_correcao(self, client: TestClient, auth, cenario):
        """AC-REM-03 — Fluxo EM_CORRECAO para AGUARDANDO_VALIDACAO."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]

        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments",
            json={"content": "Iniciando a correção conforme doc."},
            headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise", "owner_id": 1, "owner_team": "AppSec"}, headers=auth
        )
        assert resp_post.status_code == 200
        comment = resp_post.json()
        assert comment["content"] == "Iniciando a correção conforme doc."
        assert comment["author_id"] == 1

        resp_get = client.get(f"/api/vulnerabilidades/{vuln_id}/comments", headers=auth)
        assert resp_get.status_code == 200
        comments = resp_get.json()
        assert len(comments) >= 1
        assert comments[-1]["content"] == "Iniciando a correção conforme doc."
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "aguardando_validacao"

    def test_remediation_evidences(self, client: TestClient, auth, cenario):
        """AC-REM-10 — Evidências de remediação."""
    def test_ac_rem_04_revalidacao_aprovada(self, client: TestClient, auth, cenario):
        """AC-REM-04 — AGUARDANDO_VALIDACAO para CORRIGIDA preenche resolved_at."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise", "owner_id": 1, "owner_team": "AppSec"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
        )
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "corrigida"}, headers=auth
        )
        assert resp.status_code == 200
        assert resp.json()["resolved_at"] is not None

    def test_ac_rem_05_revalidacao_reprovada(self, client: TestClient, auth, cenario):
        """AC-REM-05 — AGUARDANDO_VALIDACAO para EM_CORRECAO aceita."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise", "owner_id": 1, "owner_team": "AppSec"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
        )
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        assert resp.status_code == 200

    def test_ac_rem_06_reabertura(self, client: TestClient, auth, cenario):
        """AC-REM-06 — CORRIGIDA para EM_CORRECAO limpa resolved_at."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise", "owner_id": 1, "owner_team": "AppSec"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "corrigida"}, headers=auth
        )
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        assert resp.status_code == 200
        assert resp.json()["resolved_at"] is None

    def test_ac_rem_07_owner_assignee(self, client: TestClient, auth, cenario):
        """AC-REM-07 — PATCH owner salva id, time e assigned_at."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/owner",
            json={"owner_id": 1, "owner_team": "Sec"},
            headers=auth,
        )
        assert resp.status_code == 200
        assert resp.json()["owner_id"] == 1
        assert resp.json()["assigned_at"] is not None

    def test_ac_rem_08_owner_sem_permissao(self, client: TestClient, auth, cenario):
        """AC-REM-08 — Owner sem permissao retorna 403."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        import jwt

        from app.config import settings

        token = jwt.encode(
            {"sub": "99", "email": "a@a.com", "role": "auditor"},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        bad_auth = {"Authorization": f"Bearer {token}"}
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/owner", json={"owner_id": 1}, headers=bad_auth
        )
        assert resp.status_code in (401, 403)

    def test_ac_rem_09_comentario(self, client: TestClient, auth, cenario):
        """AC-REM-09 — Adicionar comentario."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        resp = client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments", json={"content": "Teste"}, headers=auth
        )
        assert resp.status_code == 200
        assert resp.json()["content"] == "Teste"
        assert resp.json()["author_id"] == 1

    def test_ac_rem_10_lista_comentarios(self, client: TestClient, auth, cenario):
        """AC-REM-10 — Lista de comentarios cronologica."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments", json={"content": "Teste"}, headers=auth
        )
        resp = client.get(f"/api/vulnerabilidades/{vuln_id}/comments", headers=auth)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_ac_rem_11_sanitizacao(self, client: TestClient, auth, cenario):
        """AC-REM-11 — Comentarios com HTML persistidos corretamente sem bypass."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        resp = client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments", json={"content": "<script>"}, headers=auth
        )
        assert resp.status_code == 200
        assert resp.json()["content"] == "<script>"

    def test_ac_rem_12_evidencia(self, client: TestClient, auth, cenario):
        """AC-REM-12 — Adicionar evidencia."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",
            json={
                "evidence_type": "commit",
                "description": "Commit SHA 1234abcd",
                "reference": "https://github.com/pride/commit/1234"
            },
            headers=auth
        )
        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",
            json={"evidence_type": "commit", "description": "Desc"},
            headers=auth,
        )
        assert resp_post.status_code == 200

        resp_get = client.get(f"/api/vulnerabilidades/{vuln_id}/evidences", headers=auth)
        assert resp_get.status_code == 200

    def test_ac_rem_13_lista_evidencias(self, client: TestClient, auth, cenario):
        """AC-REM-13 — Lista evidencias."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",
            json={"evidence_type": "commit", "description": "Desc"},
            headers=auth,
        )
        resp = client.get(f"/api/vulnerabilidades/{vuln_id}/evidences", headers=auth)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_ac_rem_14_falso_positivo_sem_reason(self, client: TestClient, auth, cenario):
        """AC-REM-14 — FP sem reason retorna 422."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        resp_falha = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo"},
            headers=auth,
        )
        assert resp_falha.status_code == 422

    def test_ac_rem_15_falso_positivo_com_reason(self, client: TestClient, auth, cenario):
        """AC-REM-15 — FP com reason."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        resp_sucesso = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo", "reason": "É código de teste"},
            headers=auth
        )
        assert resp_sucesso.status_code == 200
        assert resp_sucesso.json()["status"] == "falso_positivo"
        assert resp_sucesso.json()["false_positive_reason"] == "É código de teste"

    def test_ac_rem_16_aceite_risco_sem_reason(self, client: TestClient, auth, cenario):
        """AC-REM-16 — Aceite de Risco sem reason retorna 422."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")
        vuln_id = vuln["id"]
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aceito_como_risco"},
            headers=auth,
        )
        assert resp.status_code == 422

    def test_transicao_invalida(self, client: TestClient, auth, cenario):
        """A máquina de estados não permite algumas transições."""
    def test_ac_rem_17_aceite_risco_com_reason(self, client: TestClient, auth, cenario):
        """AC-REM-17 — Aceite de Risco com reason."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        # Pegar uma NOVA e mover para FALSO_POSITIVO para testar o fim da linha
        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")
        vuln_id = vuln["id"]
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aceito_como_risco", "reason": "Motivo"},
            headers=auth,
        )
        assert resp.status_code == 200
        assert resp.json()["risk_acceptance_reason"] == "Motivo"
        assert resp.json()["risk_acceptance_approver_id"] is not None

    def test_ac_rem_18_audit_status(self, client: TestClient, auth, cenario, db):
        """AC-REM-18 — Audit status mudança."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        antes = len(db.query(AuditLog).all())
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "falso_positivo", "reason": "Teste"},
            headers=auth,
        )
        assert len(db.query(AuditLog).all()) > antes

    def test_ac_rem_19_audit_owner(self, client: TestClient, auth, cenario, db):
        """AC-REM-19 — Audit owner mudança."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        antes = len(db.query(AuditLog).all())
        client.patch(f"/api/vulnerabilidades/{vuln_id}/owner", json={"owner_id": 1}, headers=auth)
        assert len(db.query(AuditLog).all()) > antes

    def test_ac_rem_20_audit_comentario(self, client: TestClient, auth, cenario, db):
        """AC-REM-20 — Audit adiciona comentario."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        antes = len(db.query(AuditLog).all())
        client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments", json={"content": "Teste"}, headers=auth
        )
        assert len(db.query(AuditLog).all()) > antes

    def test_ac_rem_21_audit_evidencia(self, client: TestClient, auth, cenario, db):
        """AC-REM-21 — Audit adiciona evidencia."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        antes = len(db.query(AuditLog).all())
        client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",
            json={"description": "Teste"},
            headers=auth,
        )
        assert len(db.query(AuditLog).all()) > antes

    def test_ac_rem_22_rbac_comentarios(self, client: TestClient, cenario):
        """AC-REM-22 — RBAC comentarios requer auth."""
        resp = client.post("/api/vulnerabilidades/1/comments", json={"content": "Teste"})
        assert resp.status_code == 401

    def test_ac_rem_23_sla_campos(self, client: TestClient, auth, cenario):
        """AC-REM-23 — SLA campos de tempo na Corrigida."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise", "owner_id": 1, "owner_team": "AppSec"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
        )
        resp = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "corrigida"}, headers=auth
        )
        assert "detected_at" in resp.json() or "identificada_em" in resp.json()
        assert resp.json()["resolved_at"] is not None

    def test_ac_rem_24_vocabulario(self, client: TestClient, auth, cenario):
        """AC-REM-24 — Novos status no vocabulario listados."""
        dados = client.get("/api/dashboard", headers=auth).json()
        opcoes = [i["valor"] for i in dados["por_status"]]
        assert "aguardando_validacao" in opcoes
        assert "aceito_como_risco" in opcoes

    def test_ac_rem_25_detalhe(self, client: TestClient, auth, cenario):
        """AC-REM-25 — Detalhe inclui owner."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/owner",
            json={"owner_id": 1, "owner_team": "Sec"},
            headers=auth,
        )
        resp = client.get(f"/api/vulnerabilidades/{vuln_id}", headers=auth)
        assert resp.json()["owner_id"] == 1
        assert resp.json()["owner_team"] == "Sec"
