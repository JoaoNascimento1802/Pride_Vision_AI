# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes do fluxo de ingestão: upload, correlação, classificação e persistência.

Cobrem SDD/03-ingestao.md, mais os ACs de fluxo ponta a ponta de
SDD/01-visao-geral.md que só aparecem quando os dois relatórios se encontram.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from tests.dados import (
    NUCLEI_COM_LINHA_INVALIDA,
    NUCLEI_INFORMATIVO,
    NUCLEI_XSS,
    SEMGREP_VAZIO,
    SEMGREP_XSS_SQLI,
    arquivo,
    arquivo_bruto,
)


def _enviar(client, auth, app_id, ferramenta, conteudo, nome=None):
    return client.post(
        f"/api/aplicacoes/{app_id}/uploads/{ferramenta}",
        headers=auth,
        files=arquivo(conteudo, nome or f"{ferramenta}.txt"),
    )


class TestUploadSemgrep:
    def test_grava_os_achados(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-01, AC-ING-08 — os achados entram e o resumo diz quantos foram."""
        r = _enviar(client, auth, aplicacao_producao["id"], "semgrep", SEMGREP_XSS_SQLI)
        assert r.status_code == 201
        assert r.json()["achados_lidos"] == 2
        assert r.json()["vulnerabilidades_totais"] == 2

    def test_arquivo_vazio_recusado(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-E1 — arquivo vazio é recusado com 422 e nada é gravado."""
        r = client.post(
            f"/api/aplicacoes/{aplicacao_producao['id']}/uploads/semgrep",
            headers=auth,
            files=arquivo("   ", "vazio.json"),
        )
        assert r.status_code == 422
        assert client.get("/api/vulnerabilidades", headers=auth).json() == []

    def test_json_invalido_recusado_com_explicacao(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-ING-E2 — JSON malformado é recusado explicando o problema de sintaxe."""
        r = _enviar(client, auth, aplicacao_producao["id"], "semgrep", "{{{ quebrado")
        assert r.status_code == 422
        assert "JSON" in r.json()["detail"]

    def test_arquivo_acima_do_limite_recusado(
        self, client: TestClient, auth, aplicacao_producao, monkeypatch
    ):
        """AC-ING-E3 — arquivo maior que o limite é recusado com 413 informando o teto."""
        from app.config import settings

        monkeypatch.setattr(settings, "MAX_UPLOAD_BYTES", 32)
        r = _enviar(client, auth, aplicacao_producao["id"], "semgrep", SEMGREP_XSS_SQLI)
        assert r.status_code == 413
        assert "limite" in r.json()["detail"].lower()

    def test_arquivo_fora_de_utf8_recusado(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-E4 — conteúdo que não é UTF-8 é recusado com 422 pedindo UTF-8."""
        r = client.post(
            f"/api/aplicacoes/{aplicacao_producao['id']}/uploads/semgrep",
            headers=auth,
            files=arquivo_bruto(b"\xff\xfe{\x00\x22", "latin.json"),
        )
        assert r.status_code == 422
        assert "UTF-8" in r.json()["detail"]

    def test_aplicacao_inexistente(self, client: TestClient, auth):
        """AC-ING-E5 — upload para aplicação que não existe responde 404."""
        r = _enviar(client, auth, 9999, "semgrep", SEMGREP_XSS_SQLI)
        assert r.status_code == 404

    def test_sem_autenticacao(self, client: TestClient, aplicacao_producao):
        """AC-INV-10 — rota sob /api/aplicacoes sem token responde 401."""
        r = client.post(
            f"/api/aplicacoes/{aplicacao_producao['id']}/uploads/semgrep",
            files=arquivo(SEMGREP_XSS_SQLI, "s.json"),
        )
        assert r.status_code == 401


class TestUploadNuclei:
    def test_grava_os_achados(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-02, AC-ING-08 — o JSONL é lido e o resumo informa o total."""
        r = _enviar(client, auth, aplicacao_producao["id"], "nuclei", NUCLEI_XSS)
        assert r.status_code == 201
        assert r.json()["achados_lidos"] == 1

    def test_avisa_sobre_linhas_descartadas(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-07, AC-ING-08 — o usuário precisa saber que parte do arquivo não entrou."""
        r = _enviar(client, auth, aplicacao_producao["id"], "nuclei", NUCLEI_COM_LINHA_INVALIDA)
        assert r.status_code == 201
        assert r.json()["achados_ignorados"] == 1
        assert r.json()["avisos"]


class TestCorrelacaoEntreUploads:
    """O cenário central: o Nuclei confirma o que o Semgrep encontrou."""

    def test_nuclei_confirma_semgrep(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-10, AC-FLUXO-06 — a confirmação cruzada aparece na vulnerabilidade."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        r = _enviar(client, auth, app_id, "nuclei", NUCLEI_XSS)

        # O XSS já existia; agora ganha confirmação em vez de virar registro novo
        assert r.json()["vulnerabilidades_totais"] == 2
        assert r.json()["vulnerabilidades_novas"] == 0

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        xss = next(v for v in vulns if v["tipo_vuln"] == "xss")
        assert xss["correlacionada"]
        assert xss["encontrada_semgrep"]
        assert xss["confirmada_nuclei"]

    def test_correlacionada_vira_critica_em_producao_exposta(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-FLUXO-01 — o fluxo ponta a ponta entrega risco calculado e justificado."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        _enviar(client, auth, app_id, "nuclei", NUCLEI_XSS)

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        xss = next(v for v in vulns if v["tipo_vuln"] == "xss")
        assert xss["risco"] == "critico"

        detalhe = client.get(f"/api/vulnerabilidades/{xss['id']}", headers=auth).json()
        assert detalhe["justificativa"]

    def test_ordem_dos_uploads_nao_importa(self, client: TestClient, auth, aplicacao_producao):
        """AC-FLUXO-E2 — a recorrelação considera os achados já gravados, não só os novos."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "nuclei", NUCLEI_XSS)
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        xss = next(v for v in vulns if v["tipo_vuln"] == "xss")
        assert xss["correlacionada"]
        assert xss["risco"] == "critico"

    def test_so_semgrep_fica_sem_confirmacao_e_nao_e_descartado(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-FLUXO-E1 — sem o Nuclei, a vulnerabilidade existe e fica marcada como tal."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        assert len(vulns) == 2
        assert all(v["encontrada_semgrep"] for v in vulns)
        assert not any(v["confirmada_nuclei"] for v in vulns)

    def test_endpoint_exibido_e_a_rota(self, client: TestClient, auth, aplicacao_producao):
        """AC-COR-12 — o Semgrep reporta o arquivo; a tela precisa mostrar a rota."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        _enviar(client, auth, app_id, "nuclei", NUCLEI_XSS)

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        xss = next(v for v in vulns if v["tipo_vuln"] == "xss")
        assert xss["endpoint"] == "/busca"


class TestReenvioDeRelatorio:
    def test_reenvio_nao_duplica(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-09 — o relatório novo substitui o anterior, não soma a ele."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        r = _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        assert r.json()["vulnerabilidades_totais"] == 2
        assert r.json()["vulnerabilidades_novas"] == 0

    def test_reenvio_preserva_o_status(self, client: TestClient, auth, aplicacao_producao):
        """
        AC-STATUS-09, AC-STATUS-10 — a ingestão não toca no acompanhamento.

        O status é trabalho do usuário; uma nova varredura não pode apagá-lo. Sem
        isso, marcar algo como "Em correção" e rodar o scanner de novo perderia o
        registro.
        """
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)

        vid = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()[0][
            "id"
        ]
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_analise"}
        )
        client.patch(
            f"/api/vulnerabilidades/{vid}/status", headers=auth, json={"status": "em_correcao"}
        )

        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)

        depois = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()
        assert depois["status"] == "em_correcao"

    def test_achado_que_sumiu_e_removido(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-09 — a plataforma reflete a varredura mais recente."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        assert (
            len(client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json())
            == 2
        )

        _enviar(client, auth, app_id, "semgrep", SEMGREP_VAZIO)
        assert client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json() == []

    def test_apenas_um_upload_por_ferramenta(self, client: TestClient, auth, aplicacao_producao):
        """AC-ING-09, AC-ING-12 — fica em vigor apenas o último relatório da ferramenta."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI, "primeiro.json")
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI, "segundo.json")

        uploads = client.get(f"/api/aplicacoes/{app_id}/uploads", headers=auth).json()
        assert len(uploads) == 1
        assert uploads[0]["nome_arquivo"] == "segundo.json"

    def test_uploads_de_ferramentas_diferentes_convivem(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-ING-12 — a listagem traz o relatório em vigor de cada ferramenta."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        _enviar(client, auth, app_id, "nuclei", NUCLEI_XSS)

        uploads = client.get(f"/api/aplicacoes/{app_id}/uploads", headers=auth).json()
        assert {u["ferramenta"] for u in uploads} == {"semgrep", "nuclei"}


def _semgrep_xss(*enderecos: tuple[str, str | None]) -> str:
    """
    Relatório do Semgrep com um XSS por endereço.

    Cada endereço é `(caminho_do_arquivo, rota)`. Com rota preenchida o endpoint
    vem dela; sem rota, do caminho do arquivo.
    """
    resultados = []
    for indice, (caminho, rota) in enumerate(enderecos):
        extra: dict[str, object] = {"message": "m", "severity": "ERROR"}
        if rota:
            extra["metadata"] = {"route": rota}
        resultados.append(
            {
                "check_id": f"regra.xss.{indice}",
                "path": caminho,
                "start": {"line": indice + 1},
                "extra": extra,
            }
        )
    return json.dumps({"results": resultados})


class TestReivindicacaoDeRegistroExistente:
    def test_dois_grupos_nao_reivindicam_a_mesma_vulnerabilidade(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """
        AC-COR-E2 — cada registro gravado é reivindicado por no máximo um grupo.

        A compatibilidade de endpoint não é transitiva: `/busca/avancada` e
        `src/views/busca.py` são ambos compatíveis com `/busca`, mas não entre si.
        Sem o controle de reivindicação, os dois grupos adotariam o mesmo registro
        e um deles sumiria da tela.
        """
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", _semgrep_xss(("a.py", "/busca")))
        assert (
            len(client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json())
            == 1
        )

        resposta = _enviar(
            client,
            auth,
            app_id,
            "semgrep",
            _semgrep_xss(("a.py", "/busca/avancada"), ("src/views/busca.py", None)),
        ).json()

        assert resposta["vulnerabilidades_totais"] == 2
        assert resposta["vulnerabilidades_novas"] == 1
        assert resposta["vulnerabilidades_atualizadas"] == 1

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        assert len({v["id"] for v in vulns}) == 2
        assert len({v["endpoint"] for v in vulns}) == 2


class TestMudancaDeContexto:
    """A prova de que o contexto de negócio entra na conta."""

    def test_mudar_para_teste_reduz_o_risco(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-08, AC-RISCO-21 — mudar o contexto reclassifica o que já estava gravado."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        _enviar(client, auth, app_id, "nuclei", NUCLEI_XSS)

        antes = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        xss_antes = next(v for v in antes if v["tipo_vuln"] == "xss")
        assert xss_antes["risco"] == "critico"

        client.patch(
            f"/api/aplicacoes/{app_id}",
            headers=auth,
            json={"ambiente": "teste", "exposicao": "interna", "importancia": "baixa"},
        )

        depois = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        xss_depois = next(v for v in depois if v["tipo_vuln"] == "xss")
        assert xss_depois["risco"] == "medio"

    def test_justificativa_acompanha_a_mudanca(self, client: TestClient, auth, aplicacao_producao):
        """AC-RISCO-21 — a justificativa é reescrita junto com o nível."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        vid = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()[0][
            "id"
        ]

        client.patch(f"/api/aplicacoes/{app_id}", headers=auth, json={"ambiente": "homologacao"})

        detalhe = client.get(f"/api/vulnerabilidades/{vid}", headers=auth).json()
        assert "homologação" in detalhe["justificativa"].lower()

    def test_mudanca_sem_contexto_nao_reclassifica(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-INV-08 — alterar campo que não é contexto de negócio não mexe no risco."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        antes = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()

        client.patch(f"/api/aplicacoes/{app_id}", headers=auth, json={"responsavel": "Outro Time"})

        depois = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        assert [v["risco"] for v in antes] == [v["risco"] for v in depois]


class TestRemocaoEmCascata:
    def test_apagar_aplicacao_apaga_vulnerabilidades(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-INV-09 — remover a aplicação remove tudo que veio dela."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "semgrep", SEMGREP_XSS_SQLI)
        assert client.get("/api/vulnerabilidades", headers=auth).json()

        client.delete(f"/api/aplicacoes/{app_id}", headers=auth)
        assert client.get("/api/vulnerabilidades", headers=auth).json() == []


class TestAchadoInformativo:
    def test_informativo_sem_evidencia_e_rebaixado(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-RISCO-10 — severidade informativa desce um degrau também no fluxo real."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, "nuclei", NUCLEI_INFORMATIVO)

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        # Só o Nuclei, produção exposta seria Alto; informativo sem evidência desce
        assert vulns[0]["risco"] == "medio"


class TestSeveridadeOriginalPreservada:
    @pytest.mark.parametrize(
        ("ferramenta", "conteudo", "esperada"),
        [
            pytest.param("semgrep", SEMGREP_XSS_SQLI, "ERROR", id="AC-ING-05-semgrep"),
            pytest.param("nuclei", NUCLEI_XSS, "high", id="AC-ING-05-nuclei"),
        ],
    )
    def test_severidade_da_ferramenta_chega_a_api(
        self, client: TestClient, auth, aplicacao_producao, ferramenta, conteudo, esperada
    ):
        """A severidade original fica exibível ao lado do risco calculado pelo PRIDE."""
        app_id = aplicacao_producao["id"]
        _enviar(client, auth, app_id, ferramenta, conteudo)

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        assert any(v["severidade_original"] == esperada for v in vulns)

    def test_ingestao_cria_entidade_de_container(self, client: TestClient, auth, aplicacao_producao):
        """AC-CONT-03 — Ingestão cria entidade de container."""
        app_id = aplicacao_producao["id"]
        TRIVY_CONTAINER = """
        {
          "SchemaVersion": 2,
          "ArtifactName": "alpine:3.15",
          "ArtifactType": "container_image",
          "Metadata": {
            "RepoDigests": [
              "registry.example.com/org/app@sha256:4edbd2beb5f79b00"
            ]
          },
          "Results": [
            {
              "Target": "alpine:3.15 (alpine 3.15.0)",
              "Vulnerabilities": [
                {
                  "VulnerabilityID": "CVE-2022-28391",
                  "PkgName": "busybox",
                  "Severity": "HIGH"
                }
              ]
            }
          ]
        }
        """
        r = _enviar(client, auth, app_id, "trivy", TRIVY_CONTAINER)
        assert r.status_code == 201

        vulns = client.get(f"/api/vulnerabilidades?aplicacao_id={app_id}", headers=auth).json()
        assert len(vulns) == 1
        vuln_id = vulns[0]["id"]

        detalhes = client.get(f"/api/vulnerabilidades/{vuln_id}", headers=auth).json()
        assert detalhes["achados"][0]["image_digest"] == "sha256:4edbd2beb5f79b00"
