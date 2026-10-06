# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
Testes do motor de risco — SDD/05-risco.md.

A classificação é o coração da plataforma e precisa ser auditável: cada
combinação de contexto tem um resultado esperado e verificado.

Cada teste cita o AC que prova. Ver `backend/tests/CLAUDE.md`.
"""

from __future__ import annotations

import pytest

from app.models.enums import Ambiente, Exposicao, Ferramenta, Importancia, Risco
from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado
from app.services.risk_engine import (
    ContextoAplicacao,
    classificar,
    severidade_predominante,
)
from tests.analise_estatica import importa_algum


def _achado(origem: Ferramenta, severidade: str = "ERROR", **extras: object) -> AchadoNormalizado:
    return AchadoNormalizado(
        origem=origem,
        tipo_vuln="xss",
        endpoint="/busca",
        severidade=severidade,
        mensagem="mensagem",
        regra_id="regra",
        **extras,  # type: ignore[arg-type]
    )


def _grupo(*origens: Ferramenta, severidade: str = "ERROR", com_evidencia: bool = True):
    achados = []
    for origem in origens:
        extras: dict[str, object] = {}
        if origem is Ferramenta.NUCLEI and com_evidencia:
            extras = {"evidencia": "payload", "http_status": 200}
        achados.append(_achado(origem, severidade, **extras))
    return GrupoCorrelacionado("xss", "/busca", achados)


def _contexto(ambiente: Ambiente, exposicao: Exposicao, importancia: Importancia):
    return ContextoAplicacao(ambiente, exposicao, importancia)


AMBAS = (Ferramenta.SEMGREP, Ferramenta.NUCLEI)
SO_SEMGREP = (Ferramenta.SEMGREP,)
SO_NUCLEI = (Ferramenta.NUCLEI,)


class TestMatrizDeRisco:
    """A tabela completa: correlação x ambiente x contexto de negócio."""

    @pytest.mark.parametrize(
        ("origens", "ambiente", "exposicao", "importancia", "esperado"),
        [
            # Confirmada pelas duas ferramentas
            pytest.param(
                AMBAS,
                Ambiente.PRODUCAO,
                Exposicao.INTERNET,
                Importancia.BAIXA,
                Risco.CRITICO,
                id="AC-RISCO-01",
            ),
            pytest.param(
                AMBAS,
                Ambiente.PRODUCAO,
                Exposicao.INTERNA,
                Importancia.ALTA,
                Risco.CRITICO,
                id="AC-RISCO-02",
            ),
            pytest.param(
                AMBAS,
                Ambiente.PRODUCAO,
                Exposicao.INTERNA,
                Importancia.BAIXA,
                Risco.ALTO,
                id="AC-RISCO-03",
            ),
            pytest.param(
                AMBAS,
                Ambiente.HOMOLOGACAO,
                Exposicao.INTERNET,
                Importancia.ALTA,
                Risco.ALTO,
                id="AC-RISCO-04-exposta",
            ),
            pytest.param(
                AMBAS,
                Ambiente.HOMOLOGACAO,
                Exposicao.INTERNA,
                Importancia.BAIXA,
                Risco.ALTO,
                id="AC-RISCO-04-interna",
            ),
            pytest.param(
                AMBAS,
                Ambiente.TESTE,
                Exposicao.INTERNET,
                Importancia.ALTA,
                Risco.MEDIO,
                id="AC-RISCO-05",
            ),
            # Encontrada por apenas uma: em producao e sempre Alto (PDF §5)
            pytest.param(
                SO_SEMGREP,
                Ambiente.PRODUCAO,
                Exposicao.INTERNET,
                Importancia.BAIXA,
                Risco.ALTO,
                id="AC-RISCO-06-internet",
            ),
            pytest.param(
                SO_SEMGREP,
                Ambiente.PRODUCAO,
                Exposicao.INTERNA,
                Importancia.ALTA,
                Risco.ALTO,
                id="AC-RISCO-06-importancia",
            ),
            pytest.param(
                SO_NUCLEI,
                Ambiente.PRODUCAO,
                Exposicao.INTERNET,
                Importancia.ALTA,
                Risco.ALTO,
                id="AC-RISCO-06-nuclei",
            ),
            pytest.param(
                SO_SEMGREP,
                Ambiente.PRODUCAO,
                Exposicao.INTERNA,
                Importancia.BAIXA,
                Risco.ALTO,
                id="AC-RISCO-07",
            ),
            pytest.param(
                SO_SEMGREP,
                Ambiente.HOMOLOGACAO,
                Exposicao.INTERNA,
                Importancia.MEDIA,
                Risco.MEDIO,
                id="AC-RISCO-08",
            ),
            pytest.param(
                SO_SEMGREP,
                Ambiente.TESTE,
                Exposicao.INTERNA,
                Importancia.BAIXA,
                Risco.BAIXO,
                id="AC-RISCO-09-semgrep",
            ),
            pytest.param(
                SO_NUCLEI,
                Ambiente.TESTE,
                Exposicao.INTERNA,
                Importancia.BAIXA,
                Risco.BAIXO,
                id="AC-RISCO-09-nuclei",
            ),
        ],
    )
    def test_combinacoes(self, origens, ambiente, exposicao, importancia, esperado):
        """A matriz da SDD/05-risco.md, linha a linha. O AC vai no id do caso."""
        resultado = classificar(_grupo(*origens), _contexto(ambiente, exposicao, importancia))
        assert resultado.risco is esperado

    def test_critico_exige_producao(self):
        """AC-RISCO-04, AC-RISCO-05 — a especificação só admite crítico em produção."""
        for ambiente in (Ambiente.HOMOLOGACAO, Ambiente.TESTE):
            resultado = classificar(
                _grupo(*AMBAS),
                _contexto(ambiente, Exposicao.INTERNET, Importancia.ALTA),
            )
            assert resultado.risco is not Risco.CRITICO

    def test_duas_ferramentas_pesam_mais_que_uma(self):
        """AC-RISCO-01, AC-RISCO-06 — confirmação dupla nunca é menos grave que a simples."""
        ordem = {Risco.CRITICO: 0, Risco.ALTO: 1, Risco.MEDIO: 2, Risco.BAIXO: 3}
        for ambiente in Ambiente:
            contexto = _contexto(ambiente, Exposicao.INTERNET, Importancia.ALTA)
            duas = classificar(_grupo(*AMBAS), contexto).risco
            uma = classificar(_grupo(*SO_SEMGREP), contexto).risco
            assert ordem[duas] <= ordem[uma]

    def test_producao_pesa_mais_que_teste(self):
        """AC-RISCO-01, AC-RISCO-05 — o mesmo achado vale mais em produção que em teste."""
        ordem = {Risco.CRITICO: 0, Risco.ALTO: 1, Risco.MEDIO: 2, Risco.BAIXO: 3}
        producao = classificar(
            _grupo(*AMBAS), _contexto(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)
        ).risco
        teste = classificar(
            _grupo(*AMBAS), _contexto(Ambiente.TESTE, Exposicao.INTERNET, Importancia.ALTA)
        ).risco
        assert ordem[producao] < ordem[teste]

    def test_contexto_de_negocio_nao_rebaixa_producao_sem_confirmacao(self):
        """
        AC-RISCO-07 — em producao sem confirmacao do Nuclei o risco e Alto, ponto.

        O PDF §5 lista duas condicoes para o Risco Alto: aplicacao em producao e
        ainda sem confirmacao pelo Nuclei. Nao qualifica por exposicao nem por
        importancia, entao o contexto de negocio nao pode rebaixar o que a
        especificacao ja fixou.
        """
        exposta = classificar(
            _grupo(*SO_SEMGREP),
            _contexto(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA),
        ).risco
        interna = classificar(
            _grupo(*SO_SEMGREP),
            _contexto(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.BAIXA),
        ).risco
        assert exposta is interna is Risco.ALTO


class TestEvidenciaComoCondicaoDoCritico:
    """
    O PDF §5 lista "O Nuclei encontra evidencia relacionada" entre as quatro
    condicoes do Critico. Sem evidencia, o topo da escala nao e alcancado.
    """

    PROD = (Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)

    def test_confirmacao_dupla_sem_evidencia_para_em_alto(self):
        """AC-RISCO-22 — confirmação dupla sem evidência é Alto, não Crítico."""
        resultado = classificar(_grupo(*AMBAS, com_evidencia=False), _contexto(*self.PROD))
        assert resultado.risco is Risco.ALTO

    def test_confirmacao_dupla_com_evidencia_chega_a_critico(self):
        """AC-RISCO-22 — a mesma entrada, com evidência, é Crítico."""
        resultado = classificar(_grupo(*AMBAS, com_evidencia=True), _contexto(*self.PROD))
        assert resultado.risco is Risco.CRITICO

    def test_elevacao_por_severidade_nao_contorna_a_evidencia(self):
        """AC-RISCO-23 — a elevação por severidade crítica para em Alto sem evidência."""
        resultado = classificar(_grupo(*SO_SEMGREP, severidade="critical"), _contexto(*self.PROD))
        assert resultado.risco is Risco.ALTO

    def test_justificativa_diz_que_falta_evidencia(self):
        """AC-RISCO-22 — o usuário precisa saber por que não chegou a Crítico."""
        resultado = classificar(_grupo(*AMBAS, com_evidencia=False), _contexto(*self.PROD))
        assert "evidência" in resultado.justificativa.lower()


class TestSeveridadeNaPrioridade:
    """
    A severidade reportada é o quinto fator da seção 4.3 da especificação.

    Ela ajusta em no máximo um degrau o nível vindo da matriz: severidade
    informativa ou baixa reduz, severidade crítica em produção relevante eleva.
    """

    PROD = (Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)

    def test_severidade_neutra_nao_ajusta(self):
        """AC-RISCO-10, AC-RISCO-11 — `ERROR`, `high` e `medium` não mexem no nível."""
        contexto = _contexto(*self.PROD)
        for severidade in ("ERROR", "high", "medium"):
            resultado = classificar(_grupo(*SO_NUCLEI, severidade=severidade), contexto)
            assert resultado.risco is Risco.ALTO, severidade

    def test_informativa_reduz_mesmo_com_evidencia(self):
        """AC-RISCO-10 — a opinião da ferramenta conta mesmo com o achado confirmado."""
        contexto = _contexto(*self.PROD)
        resultado = classificar(_grupo(*SO_NUCLEI, severidade="info", com_evidencia=True), contexto)
        assert resultado.risco is Risco.MEDIO

    def test_informativa_sem_evidencia_reduz(self):
        """AC-RISCO-10 — severidade informativa desce um degrau."""
        contexto = _contexto(*self.PROD)
        resultado = classificar(
            _grupo(*SO_NUCLEI, severidade="info", com_evidencia=False), contexto
        )
        assert resultado.risco is Risco.MEDIO

    def test_baixa_tambem_reduz(self):
        """AC-RISCO-10 — severidade `low` também desce um degrau."""
        contexto = _contexto(*self.PROD)
        assert classificar(_grupo(*SO_NUCLEI, severidade="low"), contexto).risco is Risco.MEDIO

    def test_critica_eleva_em_producao_relevante(self):
        """AC-RISCO-11 — um RCE crítico não pode empatar com um XSS médio."""
        contexto = _contexto(*self.PROD)
        assert (
            classificar(_grupo(*SO_NUCLEI, severidade="critical"), contexto).risco is Risco.CRITICO
        )

    def test_critica_nao_eleva_fora_de_producao(self):
        """AC-RISCO-12 — fora de produção não há elevação, mesmo com severidade crítica."""
        contexto = _contexto(Ambiente.HOMOLOGACAO, Exposicao.INTERNET, Importancia.ALTA)
        base = classificar(_grupo(*SO_NUCLEI, severidade="ERROR"), contexto).risco
        critica = classificar(_grupo(*SO_NUCLEI, severidade="critical"), contexto).risco
        assert base is critica is Risco.MEDIO

    def test_critica_nao_eleva_sem_relevancia_de_negocio(self):
        """AC-RISCO-12 — sem relevância para o negócio não há elevação."""
        contexto = _contexto(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.BAIXA)
        base = classificar(_grupo(*SO_NUCLEI, severidade="ERROR"), contexto).risco
        critica = classificar(_grupo(*SO_NUCLEI, severidade="critical"), contexto).risco
        assert base is critica is Risco.ALTO

    def test_nunca_passa_de_critico(self):
        """AC-RISCO-13 — a escada não passa do topo."""
        contexto = _contexto(*self.PROD)
        resultado = classificar(_grupo(*AMBAS, severidade="critical"), contexto)
        assert resultado.risco is Risco.CRITICO

    def test_nunca_desce_abaixo_de_baixo(self):
        """AC-RISCO-14 — a escada não passa do fundo."""
        contexto = _contexto(Ambiente.TESTE, Exposicao.INTERNA, Importancia.BAIXA)
        resultado = classificar(
            _grupo(*SO_SEMGREP, severidade="info", com_evidencia=False), contexto
        )
        assert resultado.risco is Risco.BAIXO

    def test_ajusta_no_maximo_um_degrau(self):
        """AC-RISCO-10, AC-RISCO-11 — nem a redução nem a elevação pulam níveis."""
        ordem = {Risco.CRITICO: 0, Risco.ALTO: 1, Risco.MEDIO: 2, Risco.BAIXO: 3}
        contexto = _contexto(*self.PROD)
        base = ordem[classificar(_grupo(*SO_NUCLEI, severidade="ERROR"), contexto).risco]
        for severidade in ("info", "low", "critical"):
            ajustado = ordem[classificar(_grupo(*SO_NUCLEI, severidade=severidade), contexto).risco]
            assert abs(ajustado - base) <= 1, severidade

    def test_justificativa_explica_o_ajuste(self):
        """AC-RISCO-15 — a justificativa diz que houve ajuste e em que sentido."""
        contexto = _contexto(*self.PROD)
        elevada = classificar(_grupo(*SO_NUCLEI, severidade="critical"), contexto)
        reduzida = classificar(_grupo(*SO_NUCLEI, severidade="info"), contexto)
        assert "elevada em um nível" in elevada.justificativa
        assert "reduzida em um nível" in reduzida.justificativa

    def test_justificativa_nao_se_contradiz(self):
        """AC-RISCO-15 — a frase da matriz não nega o nível que o ajuste produziu."""
        contexto = _contexto(*self.PROD)
        resultado = classificar(_grupo(*SO_NUCLEI, severidade="critical"), contexto)
        assert resultado.risco is Risco.CRITICO
        assert "impede classificar como crítica" not in resultado.justificativa

    def test_severidade_ausente_e_tratada_como_baixa(self):
        """AC-RISCO-E2 — severidade vazia não quebra a classificação; conta como baixa."""
        contexto = _contexto(*self.PROD)
        resultado = classificar(_grupo(*SO_NUCLEI, severidade=""), contexto)
        assert resultado.risco is Risco.MEDIO
        assert resultado.justificativa

    @pytest.mark.parametrize(
        ("portugues", "ingles"),
        [
            pytest.param("critica", "critical", id="AC-RISCO-E3-critica"),
            pytest.param("baixa", "low", id="AC-RISCO-E3-baixa"),
        ],
    )
    def test_severidades_em_portugues_e_ingles_sao_equivalentes(self, portugues, ingles):
        """AC-RISCO-E3 — o mesmo nível escrito nas duas línguas produz o mesmo risco."""
        contexto = _contexto(*self.PROD)
        assert (
            classificar(_grupo(*SO_NUCLEI, severidade=portugues), contexto).risco
            is classificar(_grupo(*SO_NUCLEI, severidade=ingles), contexto).risco
        )


class TestJustificativa:
    def test_sempre_presente(self):
        """AC-RISCO-15 — toda classificação vem com justificativa não vazia."""
        for ambiente in Ambiente:
            resultado = classificar(
                _grupo(*AMBAS), _contexto(ambiente, Exposicao.INTERNET, Importancia.ALTA)
            )
            assert len(resultado.justificativa) > 40

    def test_cita_as_duas_ferramentas_quando_correlacionada(self):
        """AC-RISCO-15 — a justificativa nomeia as ferramentas que confirmaram."""
        resultado = classificar(
            _grupo(*AMBAS), _contexto(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)
        )
        assert "Semgrep" in resultado.justificativa
        assert "Nuclei" in resultado.justificativa

    def test_cita_o_ambiente(self):
        """AC-RISCO-15 — a justificativa cita o ambiente da aplicação."""
        resultado = classificar(
            _grupo(*AMBAS), _contexto(Ambiente.HOMOLOGACAO, Exposicao.INTERNA, Importancia.BAIXA)
        )
        assert "homologação" in resultado.justificativa.lower()

    def test_explica_a_ausencia_de_confirmacao(self):
        """AC-RISCO-15 — sem confirmação cruzada, a justificativa diz isso."""
        resultado = classificar(
            _grupo(*SO_SEMGREP), _contexto(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.BAIXA)
        )
        assert "sem confirmação" in resultado.justificativa.lower()


class TestDeterminismo:
    def test_mesma_entrada_mesmo_resultado(self):
        """AC-RISCO-16 — função pura: nível e justificativa idênticos."""
        grupo = _grupo(*AMBAS)
        contexto = _contexto(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)
        primeiro = classificar(grupo, contexto)
        segundo = classificar(grupo, contexto)
        assert primeiro.risco is segundo.risco
        assert primeiro.justificativa == segundo.justificativa

    def test_grupo_vazio_e_baixo(self):
        """AC-RISCO-E1 — grupo sem achados é Baixo, com justificativa explicando."""
        vazio = GrupoCorrelacionado("xss", "/x", [])
        resultado = classificar(
            vazio, _contexto(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)
        )
        assert resultado.risco is Risco.BAIXO
        assert "sem evidência" in resultado.justificativa.lower()


class TestSeveridadePredominante:
    def test_escolhe_a_mais_grave(self):
        """AC-RISCO-19 — a severidade exibida é a mais grave do grupo."""
        grupo = GrupoCorrelacionado(
            "xss",
            "/x",
            [_achado(Ferramenta.SEMGREP, "INFO"), _achado(Ferramenta.NUCLEI, "critical")],
        )
        assert severidade_predominante(grupo) == "critical"

    def test_grupo_vazio_devolve_none(self):
        """AC-RISCO-19 — sem achado não há severidade predominante."""
        assert severidade_predominante(GrupoCorrelacionado("xss", "/x", [])) is None


class TestContextoAplicacao:
    def test_internet_e_critica_para_o_negocio(self):
        """AC-RISCO-20 — exposição à internet torna a aplicação crítica para o negócio."""
        ctx = _contexto(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.BAIXA)
        assert ctx.critica_para_o_negocio

    def test_alta_importancia_tambem(self):
        """AC-RISCO-20 — importância alta também torna a aplicação crítica."""
        ctx = _contexto(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.ALTA)
        assert ctx.critica_para_o_negocio

    def test_interna_e_pouco_importante_nao_e(self):
        """AC-RISCO-20 — interna e de importância baixa não é crítica para o negócio."""
        ctx = _contexto(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.BAIXA)
        assert not ctx.critica_para_o_negocio


class TestIsolamentoDoMotorDeRisco:
    """
    As duas proibições estruturais da regra 3 do AGENTS.md.

    O motor de risco não pode conhecer a IA nem o banco. É o que torna a
    classificação auditável e reproduzível — e é a exigência mais dura do PDF §5.
    """

    def test_motor_de_risco_nao_importa_ia(self):
        """AC-RISCO-17 — o motor de risco não importa nada de IA."""
        import app.services.risk_engine as modulo

        proibidos = importa_algum(
            modulo,
            (
                "app.services.ai_explainer",
                "app.services.ai_service",
                "openai",
                # Os dois SDKs do Gemini: o antigo continua proibido mesmo depois
                # de o produto ter migrado, para a regra não abrir brecha
                "google.generativeai",
                "google.genai",
            ),
        )
        assert not proibidos, f"o motor de risco importa IA: {sorted(proibidos)}"

    def test_motor_de_risco_nao_importa_banco_nem_rede(self):
        """AC-RISCO-18 — o motor de risco não importa SQLAlchemy nem cliente de rede."""
        import app.services.risk_engine as modulo

        proibidos = importa_algum(modulo, ("sqlalchemy", "requests", "httpx", "urllib", "socket"))
        assert not proibidos, f"o motor de risco depende de infraestrutura: {sorted(proibidos)}"
