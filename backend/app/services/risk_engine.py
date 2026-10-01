"""
risk_engine.py — Classificação de risco por regras.

IMPORTANTE: este módulo nunca importa nada de `ai_explainer`. A especificação é
explícita — "a IA não será responsável por definir o risco; a classificação será
feita pelo sistema usando regras fixas. Isso deixa o resultado mais fácil de
explicar, testar e auditar".

O que a POC fazia com duas variáveis (quais ferramentas acharam), aqui passa a
considerar também o contexto de negócio: ambiente, exposição e importância. É o
que diferencia um ASPM de um comparador de arquivos — a mesma falha vale mais em
produção exposta à internet do que num ambiente de teste interno.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.enums import Ambiente, Exposicao, Ferramenta, Importancia, Risco
from app.services.dominio import GrupoCorrelacionado

# Severidades que, sozinhas, indicam achado de baixa relevância
_SEVERIDADES_BAIXAS = frozenset({"info", "informational", "informativo", "low", "baixa", ""})

# O topo da escala das ferramentas. Só esta faixa eleva o nível, e apenas em
# contexto sensível — do contrário todo achado "high" viraria crítico.
_SEVERIDADES_MAXIMAS = frozenset({"critical", "critica", "crítica"})

# Ordem usada para subir ou descer um degrau
_ESCADA = [Risco.CRITICO, Risco.ALTO, Risco.MEDIO, Risco.BAIXO]


@dataclass(frozen=True)
class ContextoAplicacao:
    """
    Os três fatores de negócio que entram na classificação.

    É um objeto próprio, e não o modelo ORM, para o motor continuar puro e
    testável sem banco.
    """

    ambiente: Ambiente
    exposicao: Exposicao
    importancia: Importancia

    @property
    def critica_para_o_negocio(self) -> bool:
        """Exposta à internet ou de alta importância para o negócio."""
        return self.exposicao is Exposicao.INTERNET or self.importancia is Importancia.ALTA


@dataclass(frozen=True)
class ResultadoRisco:
    """Nível atribuído e a explicação de como se chegou nele."""

    risco: Risco
    justificativa: str


def _descrever_contexto(contexto: ContextoAplicacao) -> str:
    """Frase curta com o contexto, usada nas justificativas."""
    partes = [f"ambiente de {contexto.ambiente.label.lower()}"]
    if contexto.exposicao is Exposicao.INTERNET:
        partes.append("exposta à internet")
    else:
        partes.append("de acesso interno")
    partes.append(f"importância {contexto.importancia.label.lower()} para o negócio")
    return ", ".join(partes)


def _rebaixar(risco: Risco) -> Risco:
    """Desce um degrau na escala, parando em Baixo."""
    indice = _ESCADA.index(risco)
    return _ESCADA[min(indice + 1, len(_ESCADA) - 1)]


def _elevar(risco: Risco) -> Risco:
    """Sobe um degrau na escala, parando em Crítico."""
    indice = _ESCADA.index(risco)
    return _ESCADA[max(indice - 1, 0)]


def _severidades(grupo: GrupoCorrelacionado) -> list[str]:
    return [a.severidade.strip().lower() for a in grupo.achados]


def _severidade_reduz(grupo: GrupoCorrelacionado) -> bool:
    """
    True quando as ferramentas classificaram o achado como pouco relevante.

    A seção 4.3 da especificação lista a severidade reportada como um dos
    fatores da priorização. Quando toda ferramenta que viu o problema o
    considerou informativo ou baixo, essa opinião conta: o achado desce um
    degrau, mesmo havendo evidência de que é alcançável.
    """
    severidades = _severidades(grupo)
    if not severidades:
        return False
    return all(s in _SEVERIDADES_BAIXAS for s in severidades)


def _severidade_eleva(grupo: GrupoCorrelacionado, contexto: ContextoAplicacao) -> bool:
    """
    True quando uma ferramenta marcou o achado como crítico em contexto sensível.

    Um RCE crítico e um XSS médio não podem terminar empatados só porque
    compartilham o ambiente. A elevação exige as três condições juntas —
    severidade máxima, produção e relevância para o negócio — para não inflar
    a lista de críticos.
    """
    if contexto.ambiente is not Ambiente.PRODUCAO or not contexto.critica_para_o_negocio:
        return False
    return any(s in _SEVERIDADES_MAXIMAS for s in _severidades(grupo))


def _nivel_base(grupo: GrupoCorrelacionado, contexto: ContextoAplicacao) -> tuple[Risco, str]:
    """
    Aplica a matriz da seção 5 da especificação.

    Cada bloco do §5 é uma conjunção: todas as condições listadas precisam
    valer. Duas consequências que a leitura apressada perde, e que esta função
    respeita (ver `SDD/05-risco.md`):

    - "O Nuclei encontra evidência relacionada" é condição do Crítico, não
      enfeite. Confirmação dupla sem evidência não chega ao topo da escala.
    - O Risco Alto tem duas condições apenas — produção e ausência de
      confirmação pelo Nuclei. Não é qualificado por exposição nem por
      importância, então o contexto de negócio não o rebaixa.

    O §5 não cobre todas as combinações. As lacunas foram preenchidas mantendo
    a lógica dele: confirmar nas duas ferramentas sempre pesa mais que confirmar
    numa só, e produção pesa mais que homologação, que pesa mais que teste.
    """
    confirmada_pelas_duas = grupo.correlacionada
    ambiente = contexto.ambiente
    contexto_texto = _descrever_contexto(contexto)

    if confirmada_pelas_duas:
        if ambiente is Ambiente.PRODUCAO and contexto.critica_para_o_negocio:
            if grupo.tem_evidencia:
                return (
                    Risco.CRITICO,
                    "Vulnerabilidade identificada no código pelo Semgrep e confirmada na "
                    f"aplicação pelo Nuclei, em {contexto_texto}. É o cenário de maior "
                    "gravidade: a falha existe e é alcançável onde mais importa.",
                )
            return (
                Risco.ALTO,
                "Vulnerabilidade identificada no código pelo Semgrep e apontada também "
                f"pelo Nuclei, em {contexto_texto}. O Nuclei, porém, não trouxe evidência "
                "concreta — nem conteúdo extraído, nem resposta HTTP —, e a especificação "
                "exige essa evidência para o nível crítico.",
            )
        if ambiente is Ambiente.PRODUCAO:
            return (
                Risco.ALTO,
                "Vulnerabilidade identificada no código e confirmada na aplicação em "
                f"produção, porém em {contexto_texto}, o que reduz a superfície de "
                "ataque em relação a uma aplicação exposta.",
            )
        if ambiente is Ambiente.HOMOLOGACAO:
            return (
                Risco.ALTO,
                "As duas ferramentas confirmaram a falha, mas em "
                f"{contexto_texto}. O mesmo código tende a chegar em produção, então "
                "a correção deve acontecer antes da promoção.",
            )
        return (
            Risco.MEDIO,
            f"As duas ferramentas confirmaram a falha, porém em {contexto_texto}, "
            "sem impacto direto sobre dados ou usuários reais.",
        )

    # Encontrada por apenas uma das ferramentas
    if grupo.encontrada_semgrep:
        origem = "análise estática (Semgrep)"
        faltando = "sem confirmação dinâmica pelo Nuclei"
    elif grupo.confirmada_nuclei:
        origem = "varredura dinâmica (Nuclei)"
        faltando = "sem correspondência no código analisado pelo Semgrep"
    elif grupo.achado_de(Ferramenta.TRIVY):
        origem = "análise de composição (Trivy)"
        faltando = "sem confirmação de outras ferramentas"
    elif grupo.achado_de(Ferramenta.GITLEAKS):
        origem = "verificação de segredos (Gitleaks)"
        faltando = "sem confirmação de outras ferramentas"
    elif grupo.achado_de(Ferramenta.CHECKOV):
        origem = "verificação de infraestrutura (Checkov)"
        faltando = "sem confirmação de outras ferramentas"
    else:
        origem = "outra ferramenta"
        faltando = "sem confirmação"

    if ambiente is Ambiente.PRODUCAO:
        return (
            Risco.ALTO,
            f"Vulnerabilidade encontrada por {origem}, {faltando}, em {contexto_texto}. "
            "A especificação classifica como alto todo achado em produção ainda sem "
            "confirmação cruzada, qualquer que seja a exposição ou a importância.",
        )
    if ambiente is Ambiente.HOMOLOGACAO:
        return (
            Risco.MEDIO,
            f"Vulnerabilidade encontrada por {origem}, {faltando}, em {contexto_texto}.",
        )
    return (
        Risco.BAIXO,
        f"Vulnerabilidade encontrada por {origem}, {faltando}, em {contexto_texto}. "
        "Sem evidência clara de exploração e fora de um ambiente produtivo.",
    )


def classificar(grupo: GrupoCorrelacionado, contexto: ContextoAplicacao) -> ResultadoRisco:
    """
    Determina o risco de um grupo correlacionado.

    Função pura: mesma entrada, mesma saída, sem rede e sem banco. É o que
    permite auditar a classificação e reproduzi-la em teste.

    Returns:
        ResultadoRisco com o nível e a justificativa em texto, que a interface
        exibe para o usuário entender por que aquilo foi priorizado.
    """
    if not grupo.achados:
        return ResultadoRisco(
            Risco.BAIXO, "Nenhum achado associado — sem evidência para classificar."
        )

    risco, justificativa = _nivel_base(grupo, contexto)

    # Ajuste pela severidade reportada — o quinto fator da seção 4.3. No máximo
    # um degrau, e os dois sentidos são mutuamente exclusivos por construção:
    # nenhuma severidade é simultaneamente informativa e crítica.
    if _severidade_reduz(grupo):
        ajustado = _rebaixar(risco)
        if ajustado is not risco:
            complemento = (
                "Sem evidência de exploração, o achado parece apenas teórico"
                if not grupo.tem_evidencia
                else "Ainda que confirmado, a própria ferramenta o considera de baixo impacto"
            )
            return ResultadoRisco(
                ajustado,
                f"{justificativa} {complemento}, então a prioridade foi reduzida em um nível.",
            )

    elif _severidade_eleva(grupo, contexto):
        ajustado = _elevar(risco)

        # A evidência é condição do Crítico no §5. Uma regra que a elevação por
        # severidade consegue contornar por um caminho lateral não é uma regra.
        if ajustado is Risco.CRITICO and not grupo.tem_evidencia:
            return ResultadoRisco(
                risco,
                f"{justificativa} A ferramenta classificou o achado com severidade "
                "crítica, o que elevaria o nível, mas sem evidência de que a falha é "
                "alcançável a especificação não admite o nível crítico.",
            )

        if ajustado is not risco:
            return ResultadoRisco(
                ajustado,
                f"{justificativa} A ferramenta classificou o achado com severidade "
                "crítica e a aplicação está em produção com relevância para o negócio, "
                "então a prioridade foi elevada em um nível.",
            )

    return ResultadoRisco(risco, justificativa)


def severidade_predominante(grupo: GrupoCorrelacionado) -> str | None:
    """
    Maior severidade original entre os achados do grupo.

    Preservada para exibição: permite ao usuário comparar o que a ferramenta
    reportou com o que o PRIDE concluiu depois de considerar o contexto. Não
    participa da decisão de risco.
    """
    if not grupo.achados:
        return None

    ordem = {
        "critical": 0,
        "critica": 0,
        "high": 1,
        "error": 1,
        "alta": 1,
        "medium": 2,
        "warning": 2,
        "media": 2,
        "low": 3,
        "baixa": 3,
        "info": 4,
        "informational": 4,
    }

    def chave(severidade: str) -> int:
        return ordem.get(severidade.strip().lower(), 5)

    return min((a.severidade for a in grupo.achados), key=chave)
