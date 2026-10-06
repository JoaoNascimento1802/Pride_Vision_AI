# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes da listagem, dos detalhes, do acompanhamento e do dashboard.

Cobrem SDD/07-acompanhamento.md, a centralização de SDD/03-ingestao.md e o
contrato de dados da visão geral em SDD/08-interface.md.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.models.enums import StatusVulnerabilidade
from tests.dados import NUCLEI_INFORMATIVO, NUCLEI_XSS, SEMGREP_XSS_SQLI, arquivo


@pytest.fixture
def cenario(client: TestClient, auth, aplicacao_producao) -> dict[str, object]:
    """
    Aplicação em produção exposta, com os três níveis de risco presentes.

    Reproduz o caso que a plataforma existe para resolver: uma falha confirmada
    pelas duas ferramentas, uma vista só pelo código, e um achado informativo.
    """
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


class TestListagem:
    def test_ordena_do_mais_grave_ao_menos(self, client: TestClient, auth, cenario):
        """AC-FLUXO-02 — a lista responde "qual corrigir primeiro": Crítico no topo."""
        riscos = [v["risco"] for v in client.get("/api/vulnerabilidades", headers=auth).json()]
        ordem = {"critico": 0, "alto": 1, "medio": 2, "baixo": 3}
        assert riscos == sorted(riscos, key=lambda r: ordem[r])

    def test_traz_os_campos_da_tela(self, client: TestClient, auth, cenario):
        """AC-ING-13 — os cinco campos que o PDF §4.2 exige da centralização."""
        item = client.get("/api/vulnerabilidades", headers=auth).json()[0]
        for campo in (
            "tipo_vuln",
            "aplicacao_nome",
            "origens",
            "severidade_original",
            "risco_label",
            "status_label",
            "identificada_em",
        ):
            assert campo in item, campo

    def test_origens_mostram_as_ferramentas(self, client: TestClient, auth, cenario):
        """AC-ING-13, AC-FLUXO-06 — a listagem diz qual ferramenta encontrou o problema."""
        vulns = client.get("/api/vulnerabilidades", headers=auth).json()
        xss = next(v for v in vulns if v["tipo_vuln"] == "xss")
        assert set(xss["origens"]) == {"Semgrep", "Nuclei"}

    @pytest.mark.parametrize(
        ("filtro", "esperado_min"),
        [
            pytest.param("risco=critico", 1, id="AC-ING-14-risco"),
            pytest.param("status=nova", 1, id="AC-STATUS-11"),
            pytest.param("apenas_correlacionadas=true", 1, id="AC-ING-14-correlacionadas"),
        ],
    )
    def test_filtros(self, client: TestClient, auth, cenario, filtro, esperado_min):
        """Cada filtro devolve apenas os itens correspondentes."""
        assert (
            len(client.get(f"/api/vulnerabilidades?{filtro}", headers=auth).json()) >= esperado_min
        )

    def test_filtro_por_status_e_exclusivo(self, client: TestClient, auth, cenario):
        """AC-STATUS-11 — filtrar por um status não traz vulnerabilidade de outro."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "aguardando_validacao"})
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "corrigida"}
        )

        corrigidas = client.get("/api/vulnerabilidades?status=corrigida", headers=auth).json()
        assert [v["id"] for v in corrigidas] == [vid]
        assert all(v["status"] == "corrigida" for v in corrigidas)

    def test_filtro_por_aplicacao(self, client: TestClient, auth, cenario):
        """AC-ING-14 — filtrar por aplicação restringe o resultado àquela aplicação."""
        app_id = cenario["app_id"]
        todas = client.get("/api/vulnerabilidades", headers=auth).json()
        da_app = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        assert len(todas) == len(da_app)

        outra = client.get("/api/vulnerabilidades?aplicacao_id=9999", headers=auth).json()
        assert outra == []

    def test_filtro_por_tipo(self, client: TestClient, auth, cenario):
        """AC-ING-14 — filtrar por tipo devolve só aquele tipo."""
        vulns = client.get("/api/vulnerabilidades?tipo_vuln=sqli", headers=auth).json()
        assert all(v["tipo_vuln"] == "sqli" for v in vulns)

    def test_lista_vazia_sem_relatorio(self, client: TestClient, auth):
        """AC-FLUXO-05 — sem nenhum relatório enviado, a resposta é 200 com lista vazia."""
        resposta = client.get("/api/vulnerabilidades", headers=auth)
        assert resposta.status_code == 200
        assert resposta.json() == []

    def test_sem_autenticacao(self, client: TestClient):
        """AC-FLUXO-07 — listagem sem token responde 401."""
        assert client.get("/api/vulnerabilidades").status_code == 401


class TestDetalhe:
    def test_traz_achados_das_duas_ferramentas(self, client: TestClient, auth, cenario):
        """AC-FLUXO-06 — o detalhe reúne o que cada ferramenta reportou."""
        vid = client.get("/api/vulnerabilidades?risco=critico", headers=auth).json()[0]["id"]
        detalhe = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()

        origens = {a["origem"] for a in detalhe["achados"]}
        assert origens == {"semgrep", "nuclei"}

    def test_achado_semgrep_traz_arquivo_e_linha(self, client: TestClient, auth, cenario):
        """AC-ING-01 — arquivo, linha e CWE do Semgrep chegam ao detalhe."""
        vid = client.get("/api/vulnerabilidades?risco=critico", headers=auth).json()[0]["id"]
        detalhe = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()

        semgrep = next(a for a in detalhe["achados"] if a["origem"] == "semgrep")
        assert semgrep["arquivo"] == "src/views/busca.py"
        assert semgrep["linha"] == 42
        assert semgrep["cwe"] == "CWE-79"

    def test_achado_nuclei_traz_evidencia_e_status(self, client: TestClient, auth, cenario):
        """AC-ING-02 — evidência e status HTTP do Nuclei chegam ao detalhe."""
        vid = client.get("/api/vulnerabilidades?risco=critico", headers=auth).json()[0]["id"]
        detalhe = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()

        nuclei = next(a for a in detalhe["achados"] if a["origem"] == "nuclei")
        assert nuclei["http_status"] == 200
        assert nuclei["evidencia"]

    def test_traz_a_justificativa(self, client: TestClient, auth, cenario):
        """AC-RISCO-15 — o detalhe explica por que aquele risco foi atribuído."""
        vid = client.get("/api/vulnerabilidades?risco=critico", headers=auth).json()[0]["id"]
        detalhe = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()
        assert len(detalhe["justificativa"]) > 40

    def test_sem_analise_de_ia_no_inicio(self, client: TestClient, auth, cenario):
        """AC-IA-11 — a análise só existe depois de pedida; não vem da ingestão."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        detalhe = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()
        assert detalhe["analise_ia"] is None
        assert detalhe["tem_analise_ia"] is False

    def test_inexistente_da_404(self, client: TestClient, auth):
        """AC-FLUXO-E3 — detalhe de vulnerabilidade inexistente responde 404."""
        resposta = client.get("/api/vulnerabilidades/9999", headers=auth)
        assert resposta.status_code == 404
        assert "não encontrada" in resposta.json()["detail"].lower()


class TestVocabularioDeStatus:
    def test_sao_exatamente_cinco(self):
        """AC-STATUS-01 — Nova, Em análise, Em correção, Corrigida e Falso positivo."""
    def test_sao_exatamente_nove(self):
        """AC-STATUS-01 — Nova, Em análise, Em correção, Corrigida, Falso positivo, Aguardando Validação, Aceito como Risco, Duplicado, Exceção Temporária."""
        assert [s.value for s in StatusVulnerabilidade] == [
            "nova",
            "em_analise",
            "em_correcao",
            "aguardando_validacao",
            "corrigida",
            "falso_positivo",
            "aceito_como_risco",
            "excecao_temporaria",
            "duplicado",
        ]

    @pytest.mark.parametrize(
        "status, encerrada",
        [
            pytest.param(StatusVulnerabilidade.NOVA, False, id="AC-STATUS-12-nova"),
            pytest.param(StatusVulnerabilidade.EM_ANALISE, False, id="AC-STATUS-12-em-analise"),
            pytest.param(StatusVulnerabilidade.EM_CORRECAO, False, id="AC-STATUS-12-em-correcao"),
            pytest.param(StatusVulnerabilidade.AGUARDANDO_VALIDACAO, False, id="AC-STATUS-12-aguardando"),
            pytest.param(StatusVulnerabilidade.EXCECAO_TEMPORARIA, False, id="AC-STATUS-12-excecao"),
            pytest.param(StatusVulnerabilidade.CORRIGIDA, True, id="AC-STATUS-12-corrigida"),
            pytest.param(
                StatusVulnerabilidade.FALSO_POSITIVO, True, id="AC-STATUS-12-falso-positivo"
            ),
            pytest.param(StatusVulnerabilidade.FALSO_POSITIVO, True, id="AC-STATUS-12-falso-positivo"),
            pytest.param(StatusVulnerabilidade.ACEITO_COMO_RISCO, True, id="AC-STATUS-12-aceito-risco"),
            pytest.param(StatusVulnerabilidade.DUPLICADO, True, id="AC-STATUS-12-duplicado"),
        ],
    )
    def test_encerrada_separa_aberto_de_fechado(self, status, encerrada):
        """Corrigida, Falso positivo, Aceito como Risco e Duplicado saem da fila de trabalho."""
        assert status.encerrada is encerrada


class TestAcompanhamento:
    def test_nasce_como_nova(self, client: TestClient, auth, cenario):
        """AC-STATUS-02 — vulnerabilidade identificada na ingestão nasce com status Nova."""
        vulns = client.get("/api/vulnerabilidades", headers=auth).json()
        assert vulns
        assert all(v["status"] == "nova" for v in vulns)

    def test_muda_o_status(self, client: TestClient, auth, cenario):
        """AC-STATUS-03 — marcar como Em correção grava e devolve o novo status."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"})
        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status",
            headers=auth,
            json={"status": "em_correcao", "comentario": "Time web assumiu"},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "em_correcao"

    def test_corrigida_sai_da_fila_de_trabalho(self, client: TestClient, auth, cenario):
        """AC-STATUS-04 — marcada como Corrigida, deixa de contar como aberta."""
        abertas_antes = client.get("/api/dashboard", headers=auth).json()["total_abertas"]
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]

        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "corrigida"}
        )
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "aguardando_validacao"})
        r = client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "corrigida"})

        assert r.json()["status"] == "corrigida"
        assert client.get("/api/dashboard", headers=auth).json()["total_abertas"] == (
            abertas_antes - 1
        )

    def test_registra_o_historico_com_o_autor(self, client: TestClient, auth, cenario):
        """AC-STATUS-06, AC-STATUS-07 — o histórico guarda o antes, o depois e quem mudou."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"}
        )
        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status",
            headers=auth,
            json={"status": "em_correcao", "comentario": "Escaping aplicado"},
        )

        historico = r.json()["historico"]
        assert len(historico) == 3  # criação + duas mudanças
        ultimo = historico[-1]
        assert ultimo["status_anterior"] == "em_analise"
        assert ultimo["status_novo"] == "em_correcao"
        assert ultimo["usuario_nome"] == "Ana Souza"
        assert ultimo["comentario"] == "Escaping aplicado"

    def test_status_repetido_e_recusado(self, client: TestClient, auth, cenario):
        """AC-STATUS-E1 — mudar para o status atual responde 409 e não duplica histórico."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"}
        )
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"})
        antes = len(client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()["historico"])

        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"}
        )
        assert r.status_code == 409

        depois = len(client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()["historico"])
        assert depois == antes

    def test_status_invalido_recusado(self, client: TestClient, auth, cenario):
        """AC-STATUS-E2 — status fora do vocabulário responde 422."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "inventado"}
        )
        assert r.status_code == 422

    def test_vulnerabilidade_inexistente_recusada(self, client: TestClient, auth):
        """AC-STATUS-E3 — mudar status de vulnerabilidade inexistente responde 404."""
        r = client.patch(
            "/api/vulnerabilidades/9999/status", headers=auth, json={"status": "corrigida"}
        )
        assert r.status_code == 404

    def test_comentario_e_opcional(self, client: TestClient, auth, cenario):
        """AC-STATUS-E4 — mudança sem comentário é aceita e o comentário fica nulo."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"}
        )
        assert r.status_code == 200
        assert r.json()["historico"][-1]["comentario"] is None

    def test_sem_autenticacao_nao_altera(self, client: TestClient, auth, cenario):
        """AC-STATUS-E5 — mudança sem token responde 401 e nada é alterado."""
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]

        r = client.patch(f"/api/vulnerabilidades/{vid}/status", json={"status": "corrigida"})
        assert r.status_code == 401

        depois = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()
        assert depois["status"] == "nova"

    def test_falso_positivo_e_um_desfecho_valido(self, client: TestClient, auth, cenario):
        """AC-STATUS-05 — Falso positivo é desfecho válido e encerra o acompanhamento."""
        abertas_antes = client.get("/api/dashboard", headers=auth).json()["total_abertas"]
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]

        r = client.patch(
            f"/api/vulnerabilidades/{vid}/status",
            headers=auth,
            json={"status": "falso_positivo", "comentario": "Endpoint não existe mais", "reason": "Mudança via teste"},
        )
        assert r.status_code == 200
        assert r.json()["status_label"] == "Falso positivo"
        assert client.get("/api/dashboard", headers=auth).json()["total_abertas"] == (
            abertas_antes - 1
        )


class TestDashboard:
    def test_numeros_da_tela_inicial(self, client: TestClient, auth, cenario):
        """AC-UI-33 — os cinco números da visão geral vêm em uma única chamada."""
        dados = client.get("/api/dashboard", headers=auth).json()
        assert dados["total_aplicacoes"] == 1
        assert dados["total_vulnerabilidades"] >= 3
        assert dados["total_criticas"] == 1
        assert dados["total_em_correcao"] == 0
        assert dados["total_corrigidas"] == 0
        assert dados["total_abertas"] == dados["total_vulnerabilidades"]

    def test_contagem_por_risco_cobre_os_quatro_niveis(self, client: TestClient, auth, cenario):
        """AC-UI-34 — os quatro níveis vêm sempre, na ordem Crítico → Baixo."""
        dados = client.get("/api/dashboard", headers=auth).json()
        valores = [i["valor"] for i in dados["por_risco"]]
        assert valores == ["critico", "alto", "medio", "baixo"]

    def test_contagem_por_status_cobre_os_cinco(self, client: TestClient, auth, cenario):
        """AC-STATUS-08 — o dashboard traz a contagem por status."""
    def test_contagem_por_status_cobre_todos_os_nove(self, client: TestClient, auth, cenario):
        """AC-STATUS-08 — o dashboard traz a contagem por status, agora com os nove status do Remediation."""
        dados = client.get("/api/dashboard", headers=auth).json()
        assert set([i["valor"] for i in dados["por_status"]]) == {
            "nova",
            "em_analise",
            "em_correcao",
            "aguardando_validacao",
            "excecao_temporaria",
            "corrigida",
            "falso_positivo",
            "aceito_como_risco",
            "duplicado",
        }

    def test_em_correcao_reflete_a_mudanca(self, client: TestClient, auth, cenario):
        """AC-STATUS-08 — marcar como Em correção aparece no contador do dashboard."""
        assert client.get("/api/dashboard", headers=auth).json()["total_em_correcao"] == 0

        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"}
        )
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"}
        )

        dados = client.get("/api/dashboard", headers=auth).json()
        assert dados["total_em_correcao"] == 1
        assert dados["total_abertas"] == dados["total_vulnerabilidades"]

    def test_corrigida_sai_das_abertas(self, client: TestClient, auth, cenario):
        """AC-UI-33 — corrigida entra no total de corrigidas e sai do total de abertas."""
        total = client.get("/api/dashboard", headers=auth).json()["total_vulnerabilidades"]
        vid = client.get("/api/vulnerabilidades", headers=auth).json()[0]["id"]
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"})
        client.patch(f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "aguardando_validacao"})
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "corrigida"}
        )

        dados = client.get("/api/dashboard", headers=auth).json()
        assert dados["total_corrigidas"] == 1
        assert dados["total_abertas"] == total - 1

    def test_ranking_de_aplicacoes(self, client: TestClient, auth, cenario):
        """AC-UI-35 — o ranking traz nome, ambiente, exposição e as contagens."""
        ranking = client.get("/api/dashboard", headers=auth).json()["aplicacoes_em_risco"]
        assert len(ranking) == 1
        primeira = ranking[0]
        assert primeira["nome"] == "Portal do Cliente"
        assert primeira["ambiente"] == "Produção"
        assert primeira["exposicao"] == "Internet"
        assert primeira["criticas"] == 1
        assert primeira["total"] >= 3
        assert primeira["pontuacao"] > 0

    def test_dashboard_vazio_nao_quebra(self, client: TestClient, auth):
        """AC-UI-E5 — base vazia devolve zeros e ranking vazio, sem erro."""
        dados = client.get("/api/dashboard", headers=auth).json()
        assert dados["total_aplicacoes"] == 0
        assert dados["total_vulnerabilidades"] == 0
        assert dados["aplicacoes_em_risco"] == []

    def test_sem_autenticacao(self, client: TestClient):
        """AC-FLUXO-07 — dashboard sem token responde 401."""
        assert client.get("/api/dashboard").status_code == 401
