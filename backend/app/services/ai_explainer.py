# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
ai_explainer.py — A IA como assistente de segurança.

Migrado da POC e ampliado com a descrição de ticket que a especificação pede.

IMPORTANTE: este módulo nunca importa `risk_engine` nem `correlator`. A IA entra
depois que o risco já foi decidido pelas regras — ela explica o resultado, não
participa dele. A especificação lista o que a IA não pode fazer: alterar código,
fazer commit, aprovar correção sozinha, mudar a classificação ou executar
ataques. Aqui ela só recebe texto e devolve texto; não há caminho para nenhuma
dessas ações.
"""

from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.config import MODELOS_GEMINI_PADRAO, MODELOS_OPENAI_PADRAO
from app.services.data_masker import mascarar

# Termos que jamais podem aparecer no prompt, para não induzir a IA a sugerir
# ações que a especificação proíbe. Verificado por teste.
TERMOS_PROIBIDOS = [
    "commit",
    "push",
    "pull request",
    "alterar arquivo",
    "executar comando",
    "criar branch",
    "aprovar a correção",
    "executar ataque",
]


@dataclass(frozen=True)
class DadosParaAnalise:
    """
    Resumo da vulnerabilidade enviado à IA.

    É montado a partir do que já foi decidido: o risco e a justificativa chegam
    prontos, para a IA explicar a priorização em vez de opinar sobre ela.
    """

    tipo_vuln: str
    endpoint: str
    risco: str
    justificativa: str
    aplicacao_nome: str
    ambiente: str
    exposicao: str
    importancia: str
    encontrada_semgrep: bool
    confirmada_nuclei: bool
    semgrep_regra: str | None = None
    semgrep_arquivo: str | None = None
    semgrep_linha: int | None = None
    semgrep_mensagem: str | None = None
    cwe: str | None = None
    nuclei_template: str | None = None
    nuclei_url: str | None = None
    nuclei_status: int | None = None
    nuclei_evidencia: str | None = None


@dataclass(frozen=True)
class AnaliseIA:
    """Resultado devolvido pela IA."""

    explicacao: str
    impacto: str
    priorizacao: str
    sugestao: str
    validacao: str
    descricao_ticket: str


class ErroProvedorIA(RuntimeError):
    """Falha ao falar com o provedor de IA."""


class ProvedorIA(ABC):
    """Contrato mínimo de um provedor. Trocar de modelo não afeta o resto."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        """Envia o prompt e devolve a resposta em texto."""


# ---------------------------------------------------------------------------
# Modelos
#
# A solução para o problema do modelo aposentado é não depender de um nome só:
# cada provedor recebe candidatos em ordem de preferência, e o primeiro que a
# chave aceitar é o usado. Quando o usuário escolhe um modelo explicitamente, a
# lista é ignorada — escolha explícita não deve ser substituída em silêncio.
#
# As listas padrão e a leitura do ambiente vivem em `app/config.py`, com o
# histórico completo do problema. Aqui elas são apenas o valor de reserva de
# quem instancia um provedor sem dizer quais modelos quer.
# ---------------------------------------------------------------------------

MODELOS_GEMINI = MODELOS_GEMINI_PADRAO
MODELOS_OPENAI = MODELOS_OPENAI_PADRAO


def _modelo_inexistente(exc: Exception) -> bool:
    """
    True quando o erro é "este modelo não existe/não está liberado".

    Só esse caso justifica tentar o próximo candidato. Falha de credencial ou de
    cota se repetiria igual em qualquer modelo.
    """
    texto = str(exc).lower()
    return any(
        marca in texto
        for marca in ("not found", "404", "not supported", "does not exist", "unsupported model")
    )


def _candidatos(
    explicito: str | None, configurados: tuple[str, ...] | None, padroes: tuple[str, ...]
) -> list[str]:
    """
    Lista de modelos a tentar, em ordem.

    Três níveis, do mais específico ao mais genérico:

    1. `explicito` — o usuário nomeou um modelo. Vira o único candidato: se
       falhar, o erro precisa aparecer, não ser mascarado por uma substituição
       silenciosa.
    2. `configurados` — a lista que veio da configuração do ambiente.
    3. `padroes` — as listas do projeto, valor de reserva.
    """
    if explicito and explicito.strip():
        return [explicito.strip()]
    if configurados:
        return list(configurados)
    return list(padroes)


def listar_modelos_gemini(cliente: Any) -> list[str]:
    """
    Modelos que a chave atual consegue usar para gerar texto.

    Serve para enriquecer a mensagem de erro: descobrir o nome correto do modelo
    é a parte difícil de diagnosticar, e a resposta está a uma chamada de
    distância.

    Recebe o cliente, não o módulo: no SDK unificado a listagem pende do cliente
    autenticado (`cliente.models.list()`), não de uma função de módulo.
    """
    try:
        disponiveis = []
        for modelo in cliente.models.list():
            # O SDK unificado chama de `supported_actions`; o antigo chamava de
            # `supported_generation_methods`. Aceitar os dois evita que a lista
            # de diagnóstico volte vazia por causa de um nome de atributo.
            acoes = (
                getattr(modelo, "supported_actions", None)
                or getattr(modelo, "supported_generation_methods", None)
                or []
            )
            if "generateContent" in acoes:
                # A API devolve "models/gemini-2.5-flash"; o usável é o final
                disponiveis.append(str(modelo.name).removeprefix("models/"))
        return sorted(disponiveis)
    except Exception:  # noqa: BLE001 — diagnóstico é melhor-esforço
        return []


class ProvedorOpenAI(ProvedorIA):
    def __init__(
        self,
        api_key: str,
        modelo: str | None = None,
        modelos: tuple[str, ...] | None = None,
    ) -> None:
        self._api_key = api_key
        self._candidatos = _candidatos(modelo, modelos, MODELOS_OPENAI)
        self._escolha_do_usuario = bool(modelo and modelo.strip())
        self._modelo_ativo: str | None = None

    @property
    def modelo(self) -> str:
        return self._modelo_ativo or self._candidatos[0]

    def completar(self, prompt: str) -> str:
        import openai  # importado só quando este provedor é usado

        cliente = openai.OpenAI(api_key=self._api_key)
        tentativas: list[str] = []

        for nome in [self._modelo_ativo] if self._modelo_ativo else self._candidatos:
            try:
                resposta = cliente.chat.completions.create(
                    model=nome,
                    messages=[{"role": "user", "content": prompt}],
                )
            except Exception as exc:  # noqa: BLE001 — a decisão é sobre o tipo do erro
                tentativas.append(nome)
                if _modelo_inexistente(exc) and not self._escolha_do_usuario:
                    continue  # modelo aposentado: tenta o próximo
                raise

            self._modelo_ativo = nome
            return resposta.choices[0].message.content or ""

        raise ErroProvedorIA(
            f"Nenhum modelo funcionou: {', '.join(tentativas)}. "
            "Defina OPENAI_MODEL no .env com um modelo que a sua conta aceite."
        )


class ProvedorGemini(ProvedorIA):
    def __init__(
        self,
        api_key: str,
        modelo: str | None = None,
        modelos: tuple[str, ...] | None = None,
    ) -> None:
        self._api_key = api_key
        self._candidatos = _candidatos(modelo, modelos, MODELOS_GEMINI)
        self._escolha_do_usuario = bool(modelo and modelo.strip())
        self._modelo_ativo: str | None = None

    @property
    def modelo(self) -> str:
        return self._modelo_ativo or self._candidatos[0]

    def completar(self, prompt: str) -> str:
        # SDK unificado `google-genai`. O antigo `google-generativeai` saiu de
        # suporte em 30/11/2025 e o `protobuf` do qual ele depende não carrega no
        # Python 3.14 — o import morria antes de qualquer chamada. Ver AC-IA-27.
        from google import genai  # importado só quando este provedor é usado

        cliente = genai.Client(api_key=self._api_key)
        tentativas: list[str] = []

        for nome in [self._modelo_ativo] if self._modelo_ativo else self._candidatos:
            try:
                resposta = cliente.models.generate_content(model=nome, contents=prompt)
            except Exception as exc:  # noqa: BLE001 — a decisão é sobre o tipo do erro
                tentativas.append(nome)
                if _modelo_inexistente(exc) and not self._escolha_do_usuario:
                    continue

                if _modelo_inexistente(exc):
                    # Dizer quais a chave aceita transforma o erro em instrução
                    disponiveis = listar_modelos_gemini(cliente)
                    if disponiveis:
                        raise ErroProvedorIA(
                            f"O modelo '{nome}' não está disponível para esta chave. "
                            f"Modelos aceitos: {', '.join(disponiveis)}. "
                            "Ajuste GEMINI_MODEL no .env."
                        ) from exc
                raise

            self._modelo_ativo = nome
            return resposta.text or ""

        disponiveis = listar_modelos_gemini(cliente)
        detalhe = (
            f" Modelos aceitos pela sua chave: {', '.join(disponiveis)}." if disponiveis else ""
        )
        raise ErroProvedorIA(f"Nenhum modelo padrão funcionou: {', '.join(tentativas)}.{detalhe}")


def montar_contexto(dados: DadosParaAnalise) -> str:
    """Serializa os dados técnicos em texto, para depois serem mascarados."""
    linhas = [
        f"tipo_vulnerabilidade: {dados.tipo_vuln}",
        f"endpoint: {dados.endpoint}",
        f"aplicacao: {dados.aplicacao_nome}",
        f"ambiente: {dados.ambiente}",
        f"exposicao: {dados.exposicao}",
        f"importancia_negocio: {dados.importancia}",
        f"encontrada_pelo_semgrep: {'sim' if dados.encontrada_semgrep else 'nao'}",
        f"confirmada_pelo_nuclei: {'sim' if dados.confirmada_nuclei else 'nao'}",
    ]

    if dados.semgrep_regra:
        linhas.append(f"semgrep_regra: {dados.semgrep_regra}")
        linhas.append(f"semgrep_arquivo: {dados.semgrep_arquivo or ''}")
        linhas.append(f"semgrep_linha: {dados.semgrep_linha or ''}")
        linhas.append(f"semgrep_mensagem: {dados.semgrep_mensagem or ''}")
    if dados.cwe:
        linhas.append(f"cwe: {dados.cwe}")
    if dados.nuclei_template:
        linhas.append(f"nuclei_template: {dados.nuclei_template}")
        linhas.append(f"nuclei_url: {dados.nuclei_url or ''}")
        linhas.append(f"nuclei_status_http: {dados.nuclei_status or ''}")
        if dados.nuclei_evidencia:
            linhas.append(f"nuclei_evidencia: {dados.nuclei_evidencia}")

    return "\n".join(linhas)


def montar_prompt(dados: DadosParaAnalise, contexto_mascarado: str) -> str:
    """
    Monta o prompt enviado ao provedor.

    O risco e a justificativa vão como fato consumado. A IA é convidada a
    explicar por que aquilo foi priorizado — não a rever a decisão.
    """
    return (
        "Você é um assistente de segurança de aplicações. Sua função é explicar "
        "vulnerabilidades para a equipe de desenvolvimento, de forma clara e "
        "objetiva, em português do Brasil.\n\n"
        "A classificação de risco abaixo já foi decidida por regras do sistema e "
        "não deve ser questionada nem alterada. Explique o problema e ajude a "
        "equipe a corrigi-lo.\n\n"
        f"Vulnerabilidade: {dados.tipo_vuln}\n"
        f"Endpoint afetado: {dados.endpoint}\n"
        f"Risco atribuído: {dados.risco}\n"
        f"Motivo da classificação: {dados.justificativa}\n\n"
        "Dados técnicos (informações sensíveis já foram substituídas por marcadores):\n"
        f"{contexto_mascarado}\n\n"
        "Responda APENAS com um objeto JSON válido, com estas seis chaves:\n"
        "{\n"
        '  "explicacao": "o que é essa vulnerabilidade e por que ela existe aqui, em 2 a 3 frases",\n'
        '  "impacto": "o que um atacante conseguiria fazer, considerando o ambiente e a exposição informados",\n'
        '  "priorizacao": "por que este achado recebeu esse nível de risco, traduzindo o motivo '
        'da classificação em linguagem simples para quem vai corrigir",\n'
        '  "sugestao": "como corrigir, de forma concreta e aplicável ao contexto técnico apresentado",\n'
        '  "validacao": "como verificar que a correção funcionou",\n'
        '  "descricao_ticket": "descrição pronta para abrir um ticket de correção, com título e passos"\n'
        "}\n\n"
        "Não inclua texto antes ou depois do JSON."
    )


def _limpar_cercas(texto: str) -> str:
    """Remove cercas de bloco de código que alguns modelos acrescentam."""
    limpo = texto.strip()
    if not limpo.startswith("```"):
        return limpo

    linhas = limpo.splitlines()
    interior = [linha for linha in linhas if not linha.strip().startswith("```")]
    return "\n".join(interior).strip()


def interpretar_resposta(texto: str) -> AnaliseIA:
    """
    Interpreta a resposta do provedor.

    Raises:
        ErroProvedorIA: se a resposta não for um JSON utilizável. Quem chama
        decide o que fazer — o pipeline nunca para por causa disso.
    """
    try:
        dados = json.loads(_limpar_cercas(texto))
    except json.JSONDecodeError as exc:
        raise ErroProvedorIA(f"A resposta da IA não é um JSON válido: {exc}") from exc

    if not isinstance(dados, dict):
        raise ErroProvedorIA("A resposta da IA não é um objeto JSON.")

    return AnaliseIA(
        explicacao=str(dados.get("explicacao", "")).strip(),
        impacto=str(dados.get("impacto", "")).strip(),
        priorizacao=str(dados.get("priorizacao", "")).strip(),
        sugestao=str(dados.get("sugestao", "")).strip(),
        validacao=str(dados.get("validacao", "")).strip(),
        descricao_ticket=str(dados.get("descricao_ticket", "")).strip(),
    )


def analisar(
    provedor: ProvedorIA,
    dados: DadosParaAnalise,
    nomes_internos: list[str] | None = None,
) -> AnaliseIA:
    """
    Produz a análise de uma vulnerabilidade já classificada.

    Ordem: serializar → mascarar → montar prompt → chamar → interpretar. O
    mascaramento acontece antes de qualquer envio, conforme a especificação.

    Raises:
        ErroProvedorIA: falha de comunicação ou resposta inutilizável.
    """
    contexto = mascarar(montar_contexto(dados), nomes_internos)
    prompt = montar_prompt(dados, contexto)

    try:
        resposta = provedor.completar(prompt)
    except Exception as exc:  # noqa: BLE001 — qualquer falha do SDK vira a mesma coisa
        print(f"[ERROR] Falha ao chamar o provedor de IA: {exc}", file=sys.stderr)
        raise ErroProvedorIA(f"Falha na comunicação com o provedor de IA: {exc}") from exc

    return interpretar_resposta(resposta)
