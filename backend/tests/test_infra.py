# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes das rotas de infraestrutura, do vocabulário controlado e das proibições
estruturais — SDD/09-arquitetura.md e SDD/01-visao-geral.md.

As proibições são a parte que mais importa aqui: o PDF diz que a plataforma não
executa scanner e que a arquitetura é um monólito simples. Sem teste, essas duas
frases são só intenção.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import BASE_DIR
from app.models.enums import (
    Ambiente,
    Exposicao,
    Ferramenta,
    Importancia,
    Risco,
    StatusVulnerabilidade,
)
from tests.analise_estatica import importa_algum

# Bibliotecas de saída HTTP. Nenhum serviço do produto pode alcançar o alvo.
CLIENTES_HTTP = ("requests", "httpx", "urllib.request", "urllib3", "socket", "aiohttp")

# Infraestrutura que o PDF §9 descarta explicitamente
INFRAESTRUTURA_PROIBIDA = (
    "celery",
    "kombu",
    "redis",
    "kubernetes",
    "pika",
    "kafka",
    "memcached",
)


class TestSaude:
    def test_responde_ok(self, client: TestClient):
        """AC-ARQ-01 — a rota de saúde responde 200 com status e versão."""
        r = client.get("/api/saude")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert r.json()["versao"]

    def test_dispensa_autenticacao(self, client: TestClient):
        """AC-ARQ-01 — a hospedagem consulta esta rota sem credencial."""
        assert client.get("/api/saude").status_code == 200

    def test_informa_se_a_ia_esta_configurada(self, client: TestClient):
        """AC-ARQ-01 — a saúde diz se há chave de IA no ambiente."""
        assert isinstance(client.get("/api/saude").json()["ia_configurada"], bool)

    def test_informa_o_estado_do_banco(self, client: TestClient):
        """AC-ARQ-19 — com o banco de pé, a saúde reporta banco ok."""
        corpo = client.get("/api/saude").json()
        assert corpo["banco"] == "ok"
        assert corpo["status"] == "ok"

    def test_sobe_e_reporta_quando_o_banco_falha(self, monkeypatch):
        """AC-ARQ-19 — banco inacessível não pode derrubar a função inteira."""
        import app.main as principal

        def _explode() -> None:
            raise RuntimeError("could not connect to server: host=interno-01 user=admin")

        monkeypatch.setattr(principal, "_ERRO_BANCO", None)
        monkeypatch.setattr(principal, "criar_tabelas", _explode)

        # O `with` é o que dispara o lifespan — é lá que a falha acontece
        with TestClient(principal.app) as cliente:
            resposta = cliente.get("/api/saude")

        assert resposta.status_code == 200, "a saúde precisa responder mesmo sem banco"
        corpo = resposta.json()
        assert corpo["status"] == "degradado"
        assert "could not connect to server" in corpo["banco"]

    def test_url_invalida_nao_derruba_a_aplicacao(self, monkeypatch):
        """AC-ARQ-20 — driver ausente vira diagnóstico na saúde, não erro de import."""
        import app.database as banco
        import app.main as principal

        monkeypatch.setattr(banco, "_engine", None)
        monkeypatch.setattr(banco, "_SessionLocal", None)
        monkeypatch.setattr(banco.settings, "DATABASE_URL", "driverinexistente://u@h/d")
        monkeypatch.setattr(principal, "_ERRO_BANCO", None)

        with TestClient(principal.app) as cliente:
            corpo = cliente.get("/api/saude").json()

        assert corpo["status"] == "degradado"
        assert corpo["banco"] != "ok"

    def test_rota_sem_banco_responde_com_banco_quebrado(self, monkeypatch):
        """AC-ARQ-20 — /api/opcoes só enumera constantes; não pode cair com o banco."""
        import app.database as banco
        import app.main as principal

        monkeypatch.setattr(banco, "_engine", None)
        monkeypatch.setattr(banco, "_SessionLocal", None)
        monkeypatch.setattr(banco.settings, "DATABASE_URL", "driverinexistente://u@h/d")
        monkeypatch.setattr(principal, "_ERRO_BANCO", None)

        with TestClient(principal.app) as cliente:
            resposta = cliente.get("/api/opcoes")

        assert resposta.status_code == 200
        assert resposta.json()["ambientes"]

    def test_engine_so_nasce_no_primeiro_uso(self, monkeypatch):
        """AC-ARQ-20 — importar o módulo não pode tentar resolver o driver."""
        import app.database as banco

        monkeypatch.setattr(banco, "_engine", None)
        monkeypatch.setattr(banco, "_SessionLocal", None)
        monkeypatch.setattr(banco.settings, "DATABASE_URL", "driverinexistente://u@h/d")

        assert banco._engine is None, "o engine não pode existir antes de ser pedido"

        with pytest.raises(Exception):
            banco.obter_engine()

    def test_mascara_o_erro_do_banco(self, monkeypatch):
        """AC-ARQ-19 — a rota é pública; host e usuário do banco não podem vazar."""
        import app.main as principal

        def _explode() -> None:
            raise RuntimeError("conexao recusada em 10.2.3.4, password=hunter2")

        monkeypatch.setattr(principal, "_ERRO_BANCO", None)
        monkeypatch.setattr(principal, "criar_tabelas", _explode)

        with TestClient(principal.app) as cliente:
            banco = cliente.get("/api/saude").json()["banco"]

        assert "10.2.3.4" not in banco
        assert "hunter2" not in banco
        assert "[IP_MASCARADO]" in banco


class TestOpcoes:
    def test_traz_todos_os_vocabularios(self, client: TestClient):
        """AC-ARQ-02 — o vocabulário controlado vem inteiro em uma chamada."""
        corpo = client.get("/api/opcoes").json()
        assert set(corpo) == {
            "ambientes",
            "exposicoes",
            "importancias",
            "riscos",
            "status",
        }

    def test_cada_item_tem_valor_e_label(self, client: TestClient):
        """AC-ARQ-02 — cada opção traz o slug e o rótulo acentuado."""
        for lista in client.get("/api/opcoes").json().values():
            for item in lista:
                assert set(item) == {"valor", "label"}
                assert item["valor"] and item["label"]

    def test_riscos_vem_do_mais_grave_para_o_menos(self, client: TestClient):
        """AC-ARQ-02 — os riscos chegam na ordem em que a interface deve exibi-los."""
        valores = [r["valor"] for r in client.get("/api/opcoes").json()["riscos"]]
        assert valores == ["critico", "alto", "medio", "baixo"]

    def test_reflete_os_enums_do_dominio(self, client: TestClient):
        """AC-ARQ-02 — a rota não mantém cópia: espelha os enums do domínio."""
        corpo = client.get("/api/opcoes").json()
        assert {a["valor"] for a in corpo["ambientes"]} == {m.value for m in Ambiente}
        assert {e["valor"] for e in corpo["exposicoes"]} == {m.value for m in Exposicao}
        assert {i["valor"] for i in corpo["importancias"]} == {m.value for m in Importancia}
        assert {s["valor"] for s in corpo["status"]} == {m.value for m in StatusVulnerabilidade}


class TestEnums:
    def test_todo_enum_tem_rotulo_legivel(self):
        """AC-ARQ-02 — todo membro do vocabulário tem rótulo para exibição."""
        for enum_cls in (Ambiente, Exposicao, Importancia, Ferramenta, Risco):
            for membro in enum_cls:
                assert membro.label
                assert membro.label != membro.value or membro.value.istitle()

    def test_ordem_do_risco(self):
        """AC-ARQ-02 — a ordem de gravidade é propriedade do domínio, não da tela."""
        assert Risco.CRITICO.ordem < Risco.ALTO.ordem < Risco.MEDIO.ordem < Risco.BAIXO.ordem

    def test_status_encerrados(self):
        """AC-STATUS-12 — Corrigida e Falso positivo saem da fila; os demais não."""
        assert StatusVulnerabilidade.CORRIGIDA.encerrada
        assert StatusVulnerabilidade.FALSO_POSITIVO.encerrada
        assert not StatusVulnerabilidade.NOVA.encerrada
        assert not StatusVulnerabilidade.EM_ANALISE.encerrada
        assert not StatusVulnerabilidade.EM_CORRECAO.encerrada


class TestDocumentacao:
    def test_openapi_e_gerado(self, client: TestClient):
        """AC-ARQ-03 — o /docs é a forma de demonstrar a API sem a interface pronta."""
        r = client.get("/openapi.json")
        assert r.status_code == 200
        assert "/api/aplicacoes" in r.json()["paths"]


class TestModulosDaArquitetura:
    """Os sete módulos que o desenho do PDF §9 lista sob a API."""

    @pytest.mark.parametrize(
        ("modulo", "rota"),
        [
            pytest.param("Aplicações", "/api/aplicacoes", id="AC-ARQ-03-aplicacoes"),
            pytest.param(
                "Uploads",
                "/api/aplicacoes/{aplicacao_id}/uploads/semgrep",
                id="AC-ARQ-03-uploads",
            ),
            pytest.param(
                "Vulnerabilidades", "/api/vulnerabilidades", id="AC-ARQ-03-vulnerabilidades"
            ),
            pytest.param(
                "IA", "/api/vulnerabilidades/{vulnerabilidade_id}/analise", id="AC-ARQ-03-ia"
            ),
            pytest.param(
                "Status de correção",
                "/api/vulnerabilidades/{vulnerabilidade_id}/status",
                id="AC-ARQ-03-status",
            ),
            pytest.param("Dashboard", "/api/dashboard", id="AC-ARQ-03-dashboard"),
        ],
    )
    def test_modulo_publicado(self, client: TestClient, modulo, rota):
        """Cada módulo do desenho tem rota correspondente na API."""
        caminhos = client.get("/openapi.json").json()["paths"]
        assert rota in caminhos, f"módulo {modulo} sem rota"

    def test_correlacao_e_risco_rodam_na_ingestao(self):
        """AC-ARQ-03 — correlação e risco não são rotas: rodam dentro da ingestão."""
        import app.services.ingestion as ingestao

        importados = importa_algum(
            ingestao, ("app.services.correlator", "app.services.risk_engine")
        )
        assert importados == {"app.services.correlator", "app.services.risk_engine"}


class TestPurezaDosServicos:
    @pytest.mark.parametrize(
        "nome_modulo",
        [
            pytest.param("normalizer", id="AC-ARQ-04-normalizer"),
            pytest.param("correlator", id="AC-ARQ-04-correlator"),
            pytest.param("data_masker", id="AC-ARQ-04-data_masker"),
            pytest.param("risk_engine", id="AC-ARQ-04-risk_engine"),
        ],
    )
    def test_servico_puro_nao_conhece_persistencia(self, nome_modulo):
        """A regra de negócio não pode depender de banco: é o que a torna testável."""
        import importlib

        modulo = importlib.import_module(f"app.services.{nome_modulo}")
        assert not importa_algum(modulo, ("sqlalchemy",))


class TestSemVarredura:
    """
    A proibição mais importante do PDF §3: a plataforma **recebe** arquivos.

    Não executa Semgrep, não executa Nuclei, não faz requisição para a aplicação
    cadastrada. A URL do inventário é dado de contexto, nunca alvo.
    """

    @pytest.mark.parametrize(
        "nome_modulo",
        [
            pytest.param("ingestion", id="AC-FLUXO-03-ingestion"),
            pytest.param("correlator", id="AC-FLUXO-03-correlator"),
            pytest.param("risk_engine", id="AC-FLUXO-03-risk_engine"),
            pytest.param("normalizer", id="AC-FLUXO-03-normalizer"),
        ],
    )
    def test_servico_nao_importa_cliente_http(self, nome_modulo):
        """Sem cliente HTTP não há como alcançar o alvo — logo, não há varredura."""
        import importlib

        modulo = importlib.import_module(f"app.services.{nome_modulo}")
        proibidos = importa_algum(modulo, CLIENTES_HTTP)
        assert not proibidos, f"{nome_modulo} pode alcançar a rede: {sorted(proibidos)}"

    def test_nenhuma_rota_dispara_varredura(self, client: TestClient):
        """AC-FLUXO-04 — não existe rota de scan, execução de ferramenta ou ataque."""
        caminhos = client.get("/openapi.json").json()["paths"]
        suspeitos = [
            caminho
            for caminho in caminhos
            if any(
                termo in caminho.lower() and "runtime" not in caminho.lower()
                for termo in ("scan", "varredura", "executar", "run", "attack", "ataque")
            )
        ]
        assert not suspeitos, f"rota que sugere varredura: {suspeitos}"

    def test_achado_so_entra_por_upload(self, client: TestClient):
        """AC-FLUXO-04 — as únicas entradas de achado são os dois uploads."""
        caminhos = client.get("/openapi.json").json()["paths"]
        entradas = {
            caminho
            for caminho, metodos in caminhos.items()
            if "post" in metodos and "upload" in caminho
        }
        assert entradas == {
            "/api/aplicacoes/{aplicacao_id}/uploads/semgrep",
            "/api/aplicacoes/{aplicacao_id}/uploads/nuclei",
            "/api/aplicacoes/{aplicacao_id}/uploads/trivy",
            "/api/aplicacoes/{aplicacao_id}/uploads/gitleaks",
            "/api/aplicacoes/{aplicacao_id}/uploads/checkov",
        }


class TestMonolitoSimples:
    @staticmethod
    def _dependencias() -> list[str]:
        pyproject = tomllib.loads((Path(BASE_DIR) / "pyproject.toml").read_text(encoding="utf-8"))
        projeto = pyproject["project"]
        opcionais = projeto.get("optional-dependencies", {})
        return [
            *projeto["dependencies"],
            *(item for grupo in opcionais.values() for item in grupo),
        ]

    def test_sem_orquestrador_fila_ou_cache_distribuido(self):
        """AC-ARQ-06 — o PDF §9 descarta microserviços, Kubernetes e afins."""
        declaradas = " ".join(self._dependencias()).lower()
        encontradas = [nome for nome in INFRAESTRUTURA_PROIBIDA if nome in declaradas]
        assert not encontradas, f"dependência de infraestrutura complexa: {encontradas}"

    def test_banco_padrao_e_sqlite(self, monkeypatch):
        """AC-ARQ-05 — sem DATABASE_URL no ambiente, o banco é SQLite."""
        from app.config import Settings

        monkeypatch.delenv("DATABASE_URL", raising=False)
        assert Settings().DATABASE_URL.startswith("sqlite:///")

    def test_extra_de_email_declarado_quando_EmailStr_e_usado(self):
        """AC-ARQ-21 — EmailStr exige email-validator já na importação do schema."""
        schemas = Path(BASE_DIR) / "app" / "schemas"
        usa_emailstr = any(
            "EmailStr" in arquivo.read_text(encoding="utf-8") for arquivo in schemas.glob("*.py")
        )
        if not usa_emailstr:  # pragma: no cover — enquanto EmailStr for usado
            pytest.skip("nenhum schema usa EmailStr")

        declaradas = " ".join(self._dependencias()).replace(" ", "").lower()

        assert "pydantic[email]" in declaradas, (
            "os schemas usam EmailStr, que exige email-validator em tempo de importação. "
            "Sem o extra declarado, uma instalação limpa não consegue nem importar a "
            "aplicação — e o erro derruba tudo, não só a validação de e-mail."
        )


class TestPragmaExclusivoDoSqlite:
    """
    O PRAGMA que liga as chaves estrangeiras é dialeto do SQLite.

    Ele é registrado no evento `connect` da classe `Engine`, que dispara para
    qualquer banco. No Postgres o PRAGMA é sintaxe inválida, e o erro — mesmo
    capturado — aborta a transação: todo statement seguinte na mesma conexão
    falha com `InFailedSqlTransaction`. Sem a guarda, toda conexão Postgres nasce
    inutilizável.
    """

    def test_pragma_nao_roda_fora_do_sqlite(self):
        """AC-ARQ-18 — em outro banco o PRAGMA não é executado."""
        from app.database import _ativar_chaves_estrangeiras

        executados: list[str] = []

        class _CursorFalso:
            def execute(self, sql: str) -> None:
                executados.append(sql)

            def close(self) -> None:
                pass

        class _ConexaoFalsa:  # não é sqlite3.Connection
            def cursor(self) -> _CursorFalso:
                return _CursorFalso()

        _ativar_chaves_estrangeiras(_ConexaoFalsa(), None)

        assert executados == [], f"PRAGMA executado fora do SQLite: {executados}"

    def test_pragma_roda_no_sqlite(self):
        """AC-ARQ-18, AC-INV-09 — em SQLite as chaves estrangeiras passam a valer."""
        import sqlite3

        from app.database import _ativar_chaves_estrangeiras

        conexao = sqlite3.connect(":memory:")
        try:
            assert conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 0

            _ativar_chaves_estrangeiras(conexao, None)

            assert conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        finally:
            conexao.close()
