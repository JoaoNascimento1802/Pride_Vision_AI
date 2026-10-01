"""
ai_service.py — Liga a IA às vulnerabilidades gravadas.

Separado de `ai_explainer` de propósito: lá ficam as funções puras (montar
prompt, mascarar, interpretar resposta), aqui fica a parte que conhece banco e
configuração.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Application, Ferramenta, Vulnerability
from app.services.ai_explainer import (
    DadosParaAnalise,
    ErroProvedorIA,
    ProvedorGemini,
    ProvedorIA,
    ProvedorOpenAI,
    analisar,
)


class IANaoConfiguradaError(RuntimeError):
    """Não há chave de API para o provedor selecionado."""


def construir_provedor(nome: str | None = None) -> ProvedorIA:
    """
    Instancia o provedor configurado, com os modelos que vierem da configuração.

    Nenhum nome de modelo aparece aqui: eles vêm do `.env` ou das listas padrão
    declaradas em `app/config.py`. É o que permite corrigir um modelo aposentado
    sem tocar em código.

    Raises:
        IANaoConfiguradaError: se faltar a chave do provedor escolhido.
    """
    escolhido = (nome or settings.AI_DEFAULT_PROVIDER).strip().lower()

    if escolhido == "gemini":
        if not settings.GEMINI_API_KEY:
            raise IANaoConfiguradaError(
                "GEMINI_API_KEY não configurada. Defina a variável no .env para "
                "habilitar as explicações por IA."
            )
        return ProvedorGemini(
            api_key=settings.GEMINI_API_KEY,
            modelo=settings.GEMINI_MODEL or None,
            modelos=tuple(settings.GEMINI_MODELS),
        )

    if not settings.OPENAI_API_KEY:
        raise IANaoConfiguradaError(
            "OPENAI_API_KEY não configurada. Defina a variável no .env para "
            "habilitar as explicações por IA."
        )
    return ProvedorOpenAI(
        api_key=settings.OPENAI_API_KEY,
        modelo=settings.OPENAI_MODEL or None,
        modelos=tuple(settings.OPENAI_MODELS),
    )


def montar_dados(vulnerabilidade: Vulnerability, aplicacao: Application) -> DadosParaAnalise:
    """Reúne o que a IA precisa saber, a partir do que está gravado."""
    semgrep = vulnerabilidade.achado_de(Ferramenta.SEMGREP)
    nuclei = vulnerabilidade.achado_de(Ferramenta.NUCLEI)

    return DadosParaAnalise(
        tipo_vuln=vulnerabilidade.tipo_vuln,
        endpoint=vulnerabilidade.endpoint,
        risco=vulnerabilidade.risco.label,
        justificativa=vulnerabilidade.justificativa,
        aplicacao_nome=aplicacao.nome,
        ambiente=aplicacao.ambiente.label,
        exposicao=aplicacao.exposicao.label,
        importancia=aplicacao.importancia.label,
        encontrada_semgrep=vulnerabilidade.encontrada_semgrep,
        confirmada_nuclei=vulnerabilidade.confirmada_nuclei,
        semgrep_regra=semgrep.regra_id if semgrep else None,
        semgrep_arquivo=semgrep.arquivo if semgrep else None,
        semgrep_linha=semgrep.linha if semgrep else None,
        semgrep_mensagem=semgrep.mensagem if semgrep else None,
        cwe=semgrep.cwe if semgrep else None,
        nuclei_template=nuclei.regra_id if nuclei else None,
        nuclei_url=nuclei.url if nuclei else None,
        nuclei_status=nuclei.http_status if nuclei else None,
        nuclei_evidencia=nuclei.evidencia if nuclei else None,
    )


def gerar_analise(
    db: Session,
    vulnerabilidade: Vulnerability,
    aplicacao: Application,
    provedor: ProvedorIA | None = None,
) -> Vulnerability:
    """
    Gera e grava a análise de IA de uma vulnerabilidade.

    O provedor pode ser injetado, o que permite testar todo o caminho sem
    chamada de rede.

    Raises:
        IANaoConfiguradaError: sem chave configurada.
        ErroProvedorIA: falha de comunicação ou resposta inutilizável.
    """
    usado = provedor if provedor is not None else construir_provedor()
    analise = analisar(
        usado, montar_dados(vulnerabilidade, aplicacao), settings.PRIDE_INTERNAL_NAMES
    )

    vulnerabilidade.ia_explicacao = analise.explicacao
    vulnerabilidade.ia_impacto = analise.impacto
    vulnerabilidade.ia_priorizacao = analise.priorizacao
    vulnerabilidade.ia_sugestao = analise.sugestao
    vulnerabilidade.ia_validacao = analise.validacao
    vulnerabilidade.ia_descricao_ticket = analise.descricao_ticket
    vulnerabilidade.ia_gerada_em = datetime.now(UTC)

    db.commit()
    db.refresh(vulnerabilidade)
    return vulnerabilidade


__all__ = [
    "ErroProvedorIA",
    "IANaoConfiguradaError",
    "construir_provedor",
    "gerar_analise",
    "montar_dados",
]
