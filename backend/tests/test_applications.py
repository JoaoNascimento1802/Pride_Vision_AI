# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes do inventário de aplicações — SDD/02-inventario.md.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.dados import SEMGREP_XSS_SQLI, arquivo

APP_BASE = {
    "nome": "Sistema de Pedidos",
    "responsavel": "Time Backend",
    "ambiente": "homologacao",
    "exposicao": "interna",
    "importancia": "media",
}


class TestCriar:
    def test_cria_aplicacao(self, client: TestClient, auth):
        """AC-INV-01 — os seis campos do PDF §4.1 são gravados e devolvidos."""
        r = client.post(
            "/api/aplicacoes",
            headers=auth,
            json={**APP_BASE, "url": "https://pedidos.exemplo.com"},
        )
        assert r.status_code == 201

        corpo = r.json()
        assert corpo["id"] > 0
        assert corpo["nome"] == "Sistema de Pedidos"
        assert corpo["responsavel"] == "Time Backend"
        assert corpo["ambiente"] == "homologacao"
        assert corpo["exposicao"] == "interna"
        assert corpo["importancia"] == "media"
        assert corpo["url"] == "https://pedidos.exemplo.com"

    @pytest.mark.parametrize(
        "ambiente",
        [
            pytest.param("producao", id="AC-INV-02-producao"),
            pytest.param("homologacao", id="AC-INV-02-homologacao"),
            pytest.param("teste", id="AC-INV-02-teste"),
        ],
    )
    def test_ambientes_aceitos(self, client: TestClient, auth, ambiente):
        """O vocabulário de ambiente tem exatamente estes três valores."""
        r = client.post("/api/aplicacoes", headers=auth, json={**APP_BASE, "ambiente": ambiente})
        assert r.status_code == 201
        assert r.json()["ambiente"] == ambiente

    @pytest.mark.parametrize(
        "exposicao",
        [
            pytest.param("internet", id="AC-INV-03-internet"),
            pytest.param("interna", id="AC-INV-03-interna"),
        ],
    )
    def test_exposicoes_aceitas(self, client: TestClient, auth, exposicao):
        """O vocabulário de exposição tem exatamente estes dois valores."""
        r = client.post("/api/aplicacoes", headers=auth, json={**APP_BASE, "exposicao": exposicao})
        assert r.status_code == 201
        assert r.json()["exposicao"] == exposicao

    @pytest.mark.parametrize(
        "importancia",
        [
            pytest.param("alta", id="AC-INV-04-alta"),
            pytest.param("media", id="AC-INV-04-media"),
            pytest.param("baixa", id="AC-INV-04-baixa"),
        ],
    )
    def test_importancias_aceitas(self, client: TestClient, auth, importancia):
        """O vocabulário de importância tem exatamente estes três valores."""
        r = client.post(
            "/api/aplicacoes", headers=auth, json={**APP_BASE, "importancia": importancia}
        )
        assert r.status_code == 201
        assert r.json()["importancia"] == importancia

    def test_devolve_slug_e_rotulo(self, client: TestClient, auth):
        """AC-INV-01 — a interface usa o slug para filtrar e o rótulo para exibir."""
        r = client.post("/api/aplicacoes", headers=auth, json=APP_BASE)
        corpo = r.json()
        assert corpo["ambiente"] == "homologacao"
        assert corpo["ambiente_label"] == "Homologação"
        assert corpo["exposicao_label"] == "Interna"
        assert corpo["importancia_label"] == "Média"

    def test_url_e_opcional(self, client: TestClient, auth):
        """AC-INV-07 — sem URL o cadastro é aceito e o campo fica nulo."""
        r = client.post("/api/aplicacoes", headers=auth, json=APP_BASE)
        assert r.status_code == 201
        assert r.json()["url"] is None

    def test_espacos_em_volta_sao_removidos(self, client: TestClient, auth):
        """AC-INV-E3 — nome e responsável são gravados sem espaços nas pontas."""
        r = client.post(
            "/api/aplicacoes",
            headers=auth,
            json={**APP_BASE, "nome": "  Com Espaços  ", "responsavel": "  Time  "},
        )
        assert r.json()["nome"] == "Com Espaços"
        assert r.json()["responsavel"] == "Time"

    @pytest.mark.parametrize(
        ("campo", "valor"),
        [
            pytest.param("ambiente", "inexistente", id="AC-INV-05-ambiente"),
            pytest.param("exposicao", "talvez", id="AC-INV-05-exposicao"),
            pytest.param("importancia", "urgentissima", id="AC-INV-05-importancia"),
        ],
    )
    def test_valor_fora_do_vocabulario_recusado(self, client: TestClient, auth, campo, valor):
        """Valor fora do vocabulário controlado responde 422 e nada é gravado."""
        r = client.post("/api/aplicacoes", headers=auth, json={**APP_BASE, campo: valor})
        assert r.status_code == 422
        assert client.get("/api/aplicacoes", headers=auth).json() == []

    def test_nome_curto_recusado(self, client: TestClient, auth):
        """AC-INV-E1 — nome com menos de 2 caracteres responde 422."""
        r = client.post("/api/aplicacoes", headers=auth, json={**APP_BASE, "nome": "X"})
        assert r.status_code == 422

    def test_sem_autenticacao(self, client: TestClient):
        """AC-INV-10 — cadastro sem token responde 401."""
        assert client.post("/api/aplicacoes", json=APP_BASE).status_code == 401


class TestListar:
    def test_lista_vazia(self, client: TestClient, auth):
        """AC-INV-06 — inventário vazio devolve lista vazia, sem erro."""
        assert client.get("/api/aplicacoes", headers=auth).json() == []

    def test_lista_ordenada_por_nome(self, client: TestClient, auth):
        """AC-INV-06 — a lista vem ordenada por nome."""
        for nome in ("Zebra", "Alfa", "Meio"):
            client.post("/api/aplicacoes", headers=auth, json={**APP_BASE, "nome": nome})
        nomes = [a["nome"] for a in client.get("/api/aplicacoes", headers=auth).json()]
        assert nomes == ["Alfa", "Meio", "Zebra"]

    def test_traz_contadores_zerados(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-E4 — aplicação sem vulnerabilidade traz contadores zerados, não ausentes."""
        item = client.get("/api/aplicacoes", headers=auth).json()[0]
        assert item["total_vulnerabilidades"] == 0
        assert item["total_criticas"] == 0
        assert item["total_abertas"] == 0

    def test_traz_contexto_e_quantidade_de_vulnerabilidades(
        self, client: TestClient, auth, aplicacao_producao
    ):
        """AC-INV-06 — a tela de aplicações do PDF §7 precisa destes campos."""
        client.post(
            f"/api/aplicacoes/{aplicacao_producao['id']}/uploads/semgrep",
            headers=auth,
            files=arquivo(SEMGREP_XSS_SQLI, "s.json"),
        )

        item = client.get("/api/aplicacoes", headers=auth).json()[0]
        assert item["ambiente_label"] == "Produção"
        assert item["exposicao_label"] == "Internet"
        assert item["importancia_label"] == "Alta"
        assert item["total_vulnerabilidades"] == 2

    def test_sem_autenticacao(self, client: TestClient):
        """AC-INV-10 — listagem sem token responde 401 e não devolve inventário."""
        resposta = client.get("/api/aplicacoes")
        assert resposta.status_code == 401
        assert "nome" not in resposta.text


class TestObterEditar:
    def test_obtem_por_id(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-01 — a aplicação cadastrada é recuperável pelo identificador."""
        r = client.get(f"/api/aplicacoes/{aplicacao_producao['id']}", headers=auth)
        assert r.status_code == 200
        assert r.json()["nome"] == "Portal do Cliente"

    def test_inexistente_da_404(self, client: TestClient, auth):
        """AC-INV-E2 — consultar aplicação inexistente responde 404 em português."""
        r = client.get("/api/aplicacoes/9999", headers=auth)
        assert r.status_code == 404
        assert "não encontrada" in r.json()["detail"].lower()

    def test_edicao_parcial_preserva_o_resto(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-01 — a edição é parcial: só o campo enviado muda."""
        r = client.patch(
            f"/api/aplicacoes/{aplicacao_producao['id']}",
            headers=auth,
            json={"responsavel": "Novo Time"},
        )
        assert r.status_code == 200
        assert r.json()["responsavel"] == "Novo Time"
        assert r.json()["nome"] == "Portal do Cliente"
        assert r.json()["ambiente"] == "producao"

    def test_muda_contexto_de_negocio(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-08 — mudar o ambiente altera o contexto que o motor de risco usa."""
        r = client.patch(
            f"/api/aplicacoes/{aplicacao_producao['id']}",
            headers=auth,
            json={"ambiente": "teste", "exposicao": "interna", "importancia": "baixa"},
        )
        assert r.json()["ambiente_label"] == "Teste"
        assert r.json()["exposicao_label"] == "Interna"
        assert r.json()["importancia_label"] == "Baixa"

    def test_editar_inexistente_da_404(self, client: TestClient, auth):
        """AC-INV-E2 — editar aplicação inexistente responde 404."""
        r = client.patch("/api/aplicacoes/9999", headers=auth, json={"nome": "Novo Nome"})
        assert r.status_code == 404


class TestRemover:
    def test_remove(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-09 — a aplicação removida deixa de existir."""
        assert (
            client.delete(f"/api/aplicacoes/{aplicacao_producao['id']}", headers=auth).status_code
            == 204
        )
        assert (
            client.get(f"/api/aplicacoes/{aplicacao_producao['id']}", headers=auth).status_code
            == 404
        )

    def test_remover_inexistente_da_404(self, client: TestClient, auth):
        """AC-INV-E2 — remover aplicação inexistente responde 404."""
        assert client.delete("/api/aplicacoes/9999", headers=auth).status_code == 404


class TestResumo:
    def test_resumo_zerado(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-11 — o resumo traz as contagens por risco e por status da aplicação."""
        r = client.get(f"/api/aplicacoes/{aplicacao_producao['id']}/resumo", headers=auth)
        assert r.status_code == 200
        corpo = r.json()
        assert corpo["total"] == 0
        assert set(corpo["por_risco"]) == {"critico", "alto", "medio", "baixo"}
        assert set(corpo["por_status"]) == {
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

    def test_resumo_conta_as_vulnerabilidades(self, client: TestClient, auth, aplicacao_producao):
        """AC-INV-11 — depois da ingestão o resumo reflete o que foi encontrado."""
        client.post(
            f"/api/aplicacoes/{aplicacao_producao['id']}/uploads/semgrep",
            headers=auth,
            files=arquivo(SEMGREP_XSS_SQLI, "s.json"),
        )

        corpo = client.get(
            f"/api/aplicacoes/{aplicacao_producao['id']}/resumo", headers=auth
        ).json()
        assert corpo["total"] == 2
        assert corpo["por_status"]["nova"] == 2

    def test_resumo_de_inexistente_da_404(self, client: TestClient, auth):
        """AC-INV-E2 — resumo de aplicação inexistente responde 404."""
        assert client.get("/api/aplicacoes/9999/resumo", headers=auth).status_code == 404


class TestContextoDeNegocio:
    """A propriedade que separa Crítico de Alto na matriz de risco."""

    def test_producao_na_internet_e_critica(self, db):
        """AC-RISCO-20 — exposição à internet basta para ser crítica para o negócio."""
        from app.models import Ambiente, Application, Exposicao, Importancia

        app_obj = Application(
            nome="X",
            responsavel="Y",
            ambiente=Ambiente.PRODUCAO,
            exposicao=Exposicao.INTERNET,
            importancia=Importancia.BAIXA,
        )
        assert app_obj.critica_para_o_negocio

    def test_interna_de_alta_importancia_tambem_e(self, db):
        """AC-RISCO-20 — importância alta basta, mesmo sendo interna."""
        from app.models import Ambiente, Application, Exposicao, Importancia

        app_obj = Application(
            nome="X",
            responsavel="Y",
            ambiente=Ambiente.PRODUCAO,
            exposicao=Exposicao.INTERNA,
            importancia=Importancia.ALTA,
        )
        assert app_obj.critica_para_o_negocio

    def test_interna_de_baixa_importancia_nao_e(self, db):
        """AC-RISCO-20 — interna e pouco importante não é crítica para o negócio."""
        from app.models import Ambiente, Application, Exposicao, Importancia

        app_obj = Application(
            nome="X",
            responsavel="Y",
            ambiente=Ambiente.PRODUCAO,
            exposicao=Exposicao.INTERNA,
            importancia=Importancia.BAIXA,
        )
        assert not app_obj.critica_para_o_negocio
