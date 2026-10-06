# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes da integração de IA — SDD/06-ia.md.

Todo o caminho é exercitado com o provedor substituído, o que verifica o
contrato sem gastar chamada de rede: o que é enviado, o que é mascarado antes do
envio, o que a IA não pode fazer, e o que acontece quando o provedor falha.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import json
import sys

import pytest
from fastapi.testclient import TestClient

from app.services import ai_service
from app.services.ai_explainer import (
    MODELOS_GEMINI,
    MODELOS_OPENAI,
    TERMOS_PROIBIDOS,
    DadosParaAnalise,
    ErroProvedorIA,
    ProvedorGemini,
    ProvedorIA,
    ProvedorOpenAI,
    analisar,
    interpretar_resposta,
    montar_prompt,
)
from tests.analise_estatica import importa_algum
from tests.dados import NUCLEI_XSS, SEMGREP_XSS_SQLI, arquivo

RESPOSTA_VALIDA = json.dumps(
    {
        "explicacao": "O parâmetro de busca é refletido no HTML sem escaping.",
        "impacto": "Roubo de sessão de quem abrir o link.",
        "priorizacao": "Crítica porque as duas ferramentas confirmaram em produção exposta.",
        "sugestao": "Aplicar escaping na saída.",
        "validacao": "Reenviar o payload e conferir que sai escapado.",
        "descricao_ticket": "[XSS] Corrigir reflexão em /busca",
    },
    ensure_ascii=False,
)


class ProvedorEspiao(ProvedorIA):
    """Captura o prompt em vez de enviá-lo."""

    def __init__(self, resposta: str = RESPOSTA_VALIDA, falhar: bool = False) -> None:
        self.resposta = resposta
        self.falhar = falhar
        self.prompt: str | None = None

    def completar(self, prompt: str) -> str:
        self.prompt = prompt
        if self.falhar:
            raise ConnectionError("sem rede")
        return self.resposta


def _dados(**extras: object) -> DadosParaAnalise:
    base: dict[str, object] = {
        "tipo_vuln": "xss",
        "endpoint": "/busca",
        "risco": "Crítico",
        "justificativa": "Identificada no código e confirmada na aplicação.",
        "aplicacao_nome": "Portal do Cliente",
        "ambiente": "Produção",
        "exposicao": "Internet",
        "importancia": "Alta",
        "encontrada_semgrep": True,
        "confirmada_nuclei": True,
    }
    base.update(extras)
    return DadosParaAnalise(**base)  # type: ignore[arg-type]


class TestPrompt:
    def test_leva_o_risco_ja_decidido(self):
        """AC-IA-12 — a IA explica a priorização; não participa dela."""
        prompt = montar_prompt(_dados(), "contexto")
        assert "Risco atribuído: Crítico" in prompt
        assert "Motivo da classificação" in prompt

    def test_instrui_a_nao_alterar_a_classificacao(self):
        """AC-IA-12 — o prompt proíbe explicitamente rever a classificação."""
        prompt = montar_prompt(_dados(), "contexto").lower()
        assert "não deve ser questionada nem alterada" in prompt

    def test_nao_contem_termos_proibidos(self):
        """AC-IA-16 — nada no prompt pode induzir às ações que a especificação veta."""
        prompt = montar_prompt(_dados(), "contexto").lower()
        encontrados = [t for t in TERMOS_PROIBIDOS if t in prompt]
        assert encontrados == []

    def test_pede_as_cinco_secoes(self):
        """AC-IA-10 — o prompt pede as seis saídas que a especificação lista."""
        prompt = montar_prompt(_dados(), "contexto")
        for chave in (
            "explicacao",
            "impacto",
            "priorizacao",
            "sugestao",
            "validacao",
            "descricao_ticket",
        ):
            assert chave in prompt


class TestMascaramentoAntesDoEnvio:
    def test_ip_nao_chega_ao_provedor(self):
        """AC-IA-09 — o IP original não aparece no prompt entregue ao provedor."""
        espiao = ProvedorEspiao()
        analisar(espiao, _dados(nuclei_template="t", nuclei_url="https://192.168.0.10/busca"))
        assert "192.168.0.10" not in (espiao.prompt or "")
        assert "[IP_MASCARADO]" in (espiao.prompt or "")

    def test_nome_interno_nao_chega_ao_provedor(self):
        """AC-IA-05, AC-IA-09 — nome interno configurado não sai da plataforma."""
        espiao = ProvedorEspiao()
        analisar(espiao, _dados(aplicacao_nome="servidor-prod-01"), ["servidor-prod-01"])
        assert "servidor-prod-01" not in (espiao.prompt or "")

    def test_evidencia_com_token_e_mascarada(self):
        """AC-IA-09 — token dentro da evidência do Nuclei também é mascarado."""
        espiao = ProvedorEspiao()
        analisar(
            espiao,
            _dados(nuclei_template="t", nuclei_evidencia="Authorization: Bearer abc123def456ghi"),
        )
        assert "abc123def456ghi" not in (espiao.prompt or "")


class TestInterpretacaoDaResposta:
    def test_le_as_seis_secoes(self):
        """AC-IA-10 — a resposta produz explicação, impacto, priorização, sugestão,
        validação e descrição de ticket."""
        analise = interpretar_resposta(RESPOSTA_VALIDA)
        assert analise.explicacao.startswith("O parâmetro")
        assert analise.descricao_ticket.startswith("[XSS]")

    def test_remove_cercas_de_codigo(self):
        """AC-IA-22 — resposta envolvida em cerca de código ainda é interpretada."""
        analise = interpretar_resposta(f"```json\n{RESPOSTA_VALIDA}\n```")
        assert analise.explicacao.startswith("O parâmetro")

    def test_json_invalido_levanta_erro(self):
        """AC-IA-E1 — resposta que não é JSON vira erro de provedor, sem gravar nada."""
        with pytest.raises(ErroProvedorIA):
            interpretar_resposta("isto não é JSON")

    def test_chaves_ausentes_viram_texto_vazio(self):
        """AC-IA-E2 — chave ausente na resposta vira texto vazio, sem quebrar."""
        analise = interpretar_resposta('{"explicacao": "só isso"}')
        assert analise.explicacao == "só isso"
        assert analise.impacto == ""

    def test_falha_do_provedor_vira_erro_tratado(self):
        """AC-IA-21 — falha de comunicação vira erro tratado, não exceção crua."""
        with pytest.raises(ErroProvedorIA, match="Falha na comunicação"):
            analisar(ProvedorEspiao(falhar=True), _dados())


class TestRotaDeAnalise:
    @pytest.fixture
    def vulnerabilidade_id(self, client: TestClient, auth, aplicacao_producao) -> int:
        app_id = aplicacao_producao["id"]
        for ferramenta, conteudo in (("semgrep", SEMGREP_XSS_SQLI), ("nuclei", NUCLEI_XSS)):
            client.post(
                f"/api/aplicacoes/{app_id}/uploads/{ferramenta}",
                headers=auth,
                files=arquivo(conteudo, f"{ferramenta}.txt"),
            )
        return int(client.get("/api/vulnerabilidades?risco=critico", headers=auth).json()[0]["id"])

    def test_gera_e_grava_a_analise(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-10, AC-IA-11 — a análise é gerada e passa a acompanhar a vulnerabilidade."""
        monkeypatch.setattr(ai_service, "construir_provedor", lambda nome=None: ProvedorEspiao())

        r = client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)
        assert r.status_code == 200

        analise = r.json()["analise_ia"]
        assert analise["explicacao"]
        assert analise["descricao_ticket"]
        assert analise["gerada_em"]
        assert r.json()["tem_analise_ia"] is True

    def test_analise_persiste_entre_consultas(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-11 — a análise fica gravada e volta nas consultas seguintes."""
        monkeypatch.setattr(ai_service, "construir_provedor", lambda nome=None: ProvedorEspiao())
        client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)

        depois = client.get(f"/api/vulnerabilidades/{vulnerabilidade_id}", headers=auth).json()
        assert depois["analise_ia"]["explicacao"]

    def test_analise_nao_altera_o_risco_decidido(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-14 — risco e justificativa continuam os que as regras definiram."""
        antes = client.get(f"/api/vulnerabilidades/{vulnerabilidade_id}", headers=auth).json()

        # A IA responde tentando rebaixar o risco; isso não pode ter efeito nenhum
        resposta_intrometida = json.dumps(
            {
                "explicacao": "Na verdade isto é apenas informativo.",
                "impacto": "Nenhum.",
                "priorizacao": "Deveria ser Baixo, não Crítico.",
                "sugestao": "Ignorar.",
                "validacao": "-",
                "descricao_ticket": "-",
            },
            ensure_ascii=False,
        )
        monkeypatch.setattr(
            ai_service,
            "construir_provedor",
            lambda nome=None: ProvedorEspiao(resposta=resposta_intrometida),
        )
        client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)

        depois = client.get(f"/api/vulnerabilidades/{vulnerabilidade_id}", headers=auth).json()
        assert depois["risco"] == antes["risco"]
        assert depois["justificativa"] == antes["justificativa"]

    def test_analise_nao_altera_o_status(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-15 — a IA não aprova correção: o acompanhamento fica intacto."""
        client.patch(
            f"/api/vulnerabilidades/{vulnerabilidade_id}/status",
            headers=auth,
            json={"status": "em_analise"},
        )
        historico_antes = len(
            client.get(f"/api/vulnerabilidades/{vulnerabilidade_id}", headers=auth).json()[
                "historico"
            ]
        )

        monkeypatch.setattr(ai_service, "construir_provedor", lambda nome=None: ProvedorEspiao())
        client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)

        depois = client.get(f"/api/vulnerabilidades/{vulnerabilidade_id}", headers=auth).json()
        assert depois["status"] == "em_analise"
        assert len(depois["historico"]) == historico_antes

    def test_sem_chave_configurada_responde_503(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-20 — sem chave, a análise responde 503 e o resto segue funcionando."""

        def sem_chave(nome=None):
            raise ai_service.IANaoConfiguradaError("OPENAI_API_KEY não configurada.")

        monkeypatch.setattr(ai_service, "construir_provedor", sem_chave)

        r = client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)
        assert r.status_code == 503
        assert "OPENAI_API_KEY" in r.json()["detail"]

        # A plataforma continua respondendo normalmente sem a IA
        assert client.get("/api/vulnerabilidades", headers=auth).status_code == 200

    def test_falha_do_provedor_responde_502(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-21 — falha do provedor responde 502."""
        monkeypatch.setattr(
            ai_service, "construir_provedor", lambda nome=None: ProvedorEspiao(falhar=True)
        )
        r = client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)
        assert r.status_code == 502

    def test_falha_da_ia_nao_afeta_o_risco(
        self, client: TestClient, auth, vulnerabilidade_id, monkeypatch
    ):
        """AC-IA-21 — risco, justificativa e acompanhamento seguem válidos sem a IA."""
        monkeypatch.setattr(
            ai_service, "construir_provedor", lambda nome=None: ProvedorEspiao(falhar=True)
        )
        client.post(f"/api/vulnerabilidades/{vulnerabilidade_id}/analise", headers=auth)

        detalhe = client.get(f"/api/vulnerabilidades/{vulnerabilidade_id}", headers=auth).json()
        assert detalhe["risco"] == "critico"
        assert detalhe["justificativa"]
        assert detalhe["analise_ia"] is None

    def test_vulnerabilidade_inexistente(self, client: TestClient, auth):
        """AC-IA-E3 — pedir análise de vulnerabilidade inexistente responde 404."""
        assert client.post("/api/vulnerabilidades/9999/analise", headers=auth).status_code == 404


class TestConstruirProvedor:
    def test_openai_com_chave(self, monkeypatch):
        """AC-IA-18 — com provedor openai e chave, o provedor OpenAI é usado."""
        monkeypatch.setattr(ai_service.settings, "AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setattr(ai_service.settings, "OPENAI_API_KEY", "sk-teste")
        assert isinstance(ai_service.construir_provedor(), ProvedorOpenAI)

    def test_gemini_com_chave(self, monkeypatch):
        """AC-IA-19 — com provedor gemini e chave, o provedor Gemini é usado."""
        from app.services.ai_explainer import ProvedorGemini

        monkeypatch.setattr(ai_service.settings, "GEMINI_API_KEY", "AIza-teste")
        assert isinstance(ai_service.construir_provedor("gemini"), ProvedorGemini)

    def test_sem_chave_levanta_erro_explicativo(self, monkeypatch):
        """AC-IA-20 — sem chave, o erro diz qual variável falta."""
        monkeypatch.setattr(ai_service.settings, "AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setattr(ai_service.settings, "OPENAI_API_KEY", "")
        with pytest.raises(ai_service.IANaoConfiguradaError, match="OPENAI_API_KEY"):
            ai_service.construir_provedor()


def _openai_falso(invalidos: set[str], usados: list[str]):
    """
    Módulo `openai` simulado, com a forma mínima que `ProvedorOpenAI` usa.

    Modelos em `invalidos` respondem com a mensagem que os provedores usam para
    dizer "este modelo não existe" — é o gatilho da troca de candidato.
    """

    class _Mensagem:
        def __init__(self, conteudo: str) -> None:
            self.content = conteudo

    class _Escolha:
        def __init__(self, conteudo: str) -> None:
            self.message = _Mensagem(conteudo)

    class _Resposta:
        def __init__(self, conteudo: str) -> None:
            self.choices = [_Escolha(conteudo)]

    class _Completions:
        def create(self, model: str, messages: list[dict[str, str]]) -> _Resposta:
            usados.append(model)
            if model in invalidos:
                raise RuntimeError(f"The model `{model}` does not exist")
            return _Resposta(RESPOSTA_VALIDA)

    class _Chat:
        completions = _Completions()

    class _Cliente:
        chat = _Chat()

    class _Modulo:
        @staticmethod
        def OpenAI(api_key: str) -> _Cliente:  # noqa: N802 — nome fixado pelo SDK
            return _Cliente()

    return _Modulo


def _genai_falso(
    invalidos: set[str],
    usados: list[str],
    modelos_da_chave: list[str] | None = None,
):
    """
    Pacote `google` simulado, com a forma mínima que `ProvedorGemini` usa.

    O que entra em `sys.modules` é o pacote `google`, não `google.genai`: a forma
    de import é `from google import genai`, e o interpretador resolve isso por
    atributo do pacote.
    """

    class _Resposta:
        def __init__(self, texto: str) -> None:
            self.text = texto

    class _ModeloListado:
        def __init__(self, nome: str) -> None:
            # A API devolve o nome qualificado; o usável é o final
            self.name = f"models/{nome}"
            self.supported_actions = ["generateContent"]

    class _Models:
        def generate_content(self, model: str, contents: str) -> _Resposta:
            usados.append(model)
            if model in invalidos:
                raise RuntimeError(f"models/{model} is not found for API version v1beta")
            return _Resposta(RESPOSTA_VALIDA)

        def list(self) -> list[_ModeloListado]:
            return [_ModeloListado(nome) for nome in (modelos_da_chave or [])]

    class _Cliente:
        def __init__(self) -> None:
            self.models = _Models()

    class _Genai:
        @staticmethod
        def Client(api_key: str) -> _Cliente:  # noqa: N802 — nome fixado pelo SDK
            return _Cliente()

    class _PacoteGoogle:
        genai = _Genai

    return _PacoteGoogle


class TestModeloAposentado:
    """
    O nome de um modelo apodrece. O provedor tenta o próximo candidato — mas só
    quando a escolha não foi do usuário.
    """

    def test_modelo_aposentado_cai_para_o_proximo(self, monkeypatch):
        """AC-IA-E4 — modelo padrão inexistente faz o provedor tentar o seguinte."""
        usados: list[str] = []
        monkeypatch.setitem(sys.modules, "openai", _openai_falso({MODELOS_OPENAI[0]}, usados))

        resultado = ProvedorOpenAI("sk-teste").completar("prompt")

        assert usados == [MODELOS_OPENAI[0], MODELOS_OPENAI[1]]
        assert resultado == RESPOSTA_VALIDA

    def test_modelo_escolhido_pelo_usuario_nao_e_substituido(self, monkeypatch):
        """AC-IA-E4 — escolha explícita falha visivelmente em vez de ser trocada."""
        usados: list[str] = []
        monkeypatch.setitem(sys.modules, "openai", _openai_falso({"modelo-do-usuario"}, usados))

        with pytest.raises(RuntimeError, match="does not exist"):
            ProvedorOpenAI("sk-teste", modelo="modelo-do-usuario").completar("prompt")

        assert usados == ["modelo-do-usuario"]

    def test_fallback_percorre_a_lista_configurada(self, monkeypatch):
        """AC-IA-23 — o próximo candidato vem da lista do ambiente, não da padrão."""
        usados: list[str] = []
        monkeypatch.setitem(sys.modules, "openai", _openai_falso({"config-a"}, usados))

        resultado = ProvedorOpenAI(
            "sk-teste", modelos=("config-a", "config-b", "config-c")
        ).completar("prompt")

        assert usados == ["config-a", "config-b"]
        assert resultado == RESPOSTA_VALIDA
        assert not any(nome in MODELOS_OPENAI for nome in usados)


class TestProvedorGemini:
    """
    O caminho do Gemini com SDK simulado — o que o lado do OpenAI já tinha.

    A ausência destes testes é o que deixou o provedor quebrar em silêncio: o
    `google-generativeai` deixou de carregar no Python 3.14 (o `protobuf` dele
    não sobe) e a suíte continuou verde, porque o import é preguiçoso e nenhum
    teste chegava a executá-lo.
    """

    def test_gemini_usa_o_sdk_unificado(self, monkeypatch):
        """AC-IA-27 — a chamada passa por google.genai: Client → models.generate_content."""
        usados: list[str] = []
        monkeypatch.setitem(sys.modules, "google", _genai_falso(set(), usados))

        resultado = ProvedorGemini("AIza-teste", modelo="gemini-de-teste").completar("prompt")

        assert usados == ["gemini-de-teste"]
        assert resultado == RESPOSTA_VALIDA

    def test_produto_nao_importa_o_sdk_aposentado(self):
        """AC-IA-27 — google.generativeai saiu de suporte e não carrega no Python 3.14."""
        from pathlib import Path

        import app

        raiz = Path(app.__file__).parent
        ofensores = [
            str(caminho.relative_to(raiz))
            for caminho in raiz.rglob("*.py")
            if "google.generativeai" in caminho.read_text(encoding="utf-8")
        ]
        assert not ofensores, f"SDK aposentado ainda referenciado em: {ofensores}"

    def test_gemini_cai_para_o_proximo_modelo(self, monkeypatch):
        """AC-IA-28 — modelo recusado pela chave faz o provedor tentar o seguinte."""
        usados: list[str] = []
        monkeypatch.setitem(sys.modules, "google", _genai_falso({MODELOS_GEMINI[0]}, usados))

        resultado = ProvedorGemini("AIza-teste").completar("prompt")

        assert usados == [MODELOS_GEMINI[0], MODELOS_GEMINI[1]]
        assert resultado == RESPOSTA_VALIDA

    def test_gemini_com_modelo_fixado_nao_troca(self, monkeypatch):
        """AC-IA-28 — escolha explícita falha visivelmente em vez de ser substituída."""
        usados: list[str] = []
        monkeypatch.setitem(sys.modules, "google", _genai_falso({"gemini-do-usuario"}, usados))

        with pytest.raises(RuntimeError, match="not found"):
            ProvedorGemini("AIza-teste", modelo="gemini-do-usuario").completar("prompt")

        assert usados == ["gemini-do-usuario"]

    def test_gemini_lista_os_modelos_aceitos_no_erro(self, monkeypatch):
        """AC-IA-27 — o erro diz quais modelos a chave aceita, virando instrução."""
        usados: list[str] = []
        monkeypatch.setitem(
            sys.modules,
            "google",
            _genai_falso({"gemini-do-usuario"}, usados, modelos_da_chave=["gemini-2.5-flash"]),
        )

        with pytest.raises(ErroProvedorIA, match="gemini-2.5-flash"):
            ProvedorGemini("AIza-teste", modelo="gemini-do-usuario").completar("prompt")


class TestModeloConfiguravel:
    """
    Nenhum nome de modelo fixado no caminho de chamada: quando um provedor
    aposenta um modelo, a correção é no `.env`.
    """

    def test_construir_provedor_respeita_a_lista_configurada(self, monkeypatch):
        """AC-IA-23 — o provedor construído recebe os candidatos da configuração."""
        monkeypatch.setattr(ai_service.settings, "AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setattr(ai_service.settings, "OPENAI_API_KEY", "sk-teste")
        monkeypatch.setattr(ai_service.settings, "OPENAI_MODEL", "")
        monkeypatch.setattr(ai_service.settings, "OPENAI_MODELS", ["do-env-1", "do-env-2"])

        provedor = ai_service.construir_provedor()
        assert isinstance(provedor, ProvedorOpenAI)
        assert provedor.modelo == "do-env-1"

    def test_construir_provedor_respeita_o_modelo_explicito(self, monkeypatch):
        """AC-IA-24 — com OPENAI_MODEL definido, é ele e só ele."""
        monkeypatch.setattr(ai_service.settings, "AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setattr(ai_service.settings, "OPENAI_API_KEY", "sk-teste")
        monkeypatch.setattr(ai_service.settings, "OPENAI_MODEL", "so-este")
        monkeypatch.setattr(ai_service.settings, "OPENAI_MODELS", ["ignorado"])

        assert ai_service.construir_provedor().modelo == "so-este"

    def test_gemini_tambem_e_configuravel(self, monkeypatch):
        """AC-IA-24 — o mesmo vale para o Gemini."""
        from app.services.ai_explainer import ProvedorGemini

        monkeypatch.setattr(ai_service.settings, "GEMINI_API_KEY", "AIza-teste")
        monkeypatch.setattr(ai_service.settings, "GEMINI_MODEL", "gemini-do-usuario")

        provedor = ai_service.construir_provedor("gemini")
        assert isinstance(provedor, ProvedorGemini)
        assert provedor.modelo == "gemini-do-usuario"

    def test_saude_informa_provedor_e_modelo(self, client: TestClient, monkeypatch):
        """AC-IA-25 — descobrir qual modelo está ativo é a parte difícil do diagnóstico."""
        monkeypatch.setattr(ai_service.settings, "AI_DEFAULT_PROVIDER", "openai")
        monkeypatch.setattr(ai_service.settings, "OPENAI_MODEL", "modelo-ativo")

        corpo = client.get("/api/saude").json()
        assert corpo["provedor_ia"] == "openai"
        assert corpo["modelo_ia"] == "modelo-ativo"

    def test_nenhum_nome_de_modelo_no_construtor_de_provedores(self):
        """AC-IA-26 — os nomes vivem na configuração e nas listas padrão, em um lugar só."""
        from pathlib import Path

        import app.services.ai_service as modulo

        fonte = Path(modulo.__file__).read_text(encoding="utf-8")
        for nome in (*MODELOS_OPENAI, *MODELOS_GEMINI):
            assert nome not in fonte, f"nome de modelo fixado em ai_service.py: {nome}"


class TestIsolamento:
    """As proibições estruturais da especificação §6."""

    def test_ia_nao_importa_o_motor_de_risco(self):
        """AC-IA-13 — a IA não pode participar da decisão de risco."""
        import app.services.ai_explainer as modulo

        proibidos = importa_algum(modulo, ("app.services.risk_engine", "app.services.correlator"))
        assert not proibidos, f"a IA conhece a decisão de risco: {sorted(proibidos)}"

    def test_ia_nao_importa_execucao(self):
        """AC-IA-17 — a IA não pode executar nada: sem subprocess nem shell."""
        import app.services.ai_explainer as modulo

        proibidos = importa_algum(modulo, ("subprocess", "shutil", "pty", "multiprocessing"))
        assert not proibidos, f"a IA tem caminho para executar: {sorted(proibidos)}"
