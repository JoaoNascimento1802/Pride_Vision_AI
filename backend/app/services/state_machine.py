# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
state_machine.py — Máquina de estados do workflow de remediação.

Define as transições válidas entre os status de vulnerabilidade.
A validação acontece na camada de domínio, antes do banco, para
garantir rastreabilidade e impedir manipulações indevidas.
"""

from __future__ import annotations

from app.models.enums import StatusVulnerabilidade as S

# Mapa de transições válidas: de qual status se pode ir para quais outros
TRANSICOES_VALIDAS: dict[S, frozenset[S]] = {
    S.NOVA: frozenset({
        S.EM_ANALISE,
        S.FALSO_POSITIVO,
        S.ACEITO_COMO_RISCO,
        S.EXCECAO_TEMPORARIA,
        S.DUPLICADO,
    }),
    S.EM_ANALISE: frozenset({
        S.EM_CORRECAO,
        S.FALSO_POSITIVO,
        S.ACEITO_COMO_RISCO,
        S.EXCECAO_TEMPORARIA,
        S.DUPLICADO,
    }),
    S.EM_CORRECAO: frozenset({
        S.AGUARDANDO_VALIDACAO,
        S.FALSO_POSITIVO,
        S.ACEITO_COMO_RISCO,
        S.DUPLICADO,
    }),
    S.AGUARDANDO_VALIDACAO: frozenset({
        S.CORRIGIDA,
        S.EM_CORRECAO,  # revalidação falhou
    }),
    S.CORRIGIDA: frozenset({
        S.EM_CORRECAO,  # reabertura
    }),
    S.FALSO_POSITIVO: frozenset({
        S.NOVA,  # reabertura após revisão
    }),
    S.ACEITO_COMO_RISCO: frozenset({
        S.EM_ANALISE,  # reaberto para correção
    }),
    S.EXCECAO_TEMPORARIA: frozenset({
        S.EM_CORRECAO,
        S.NOVA,
    }),
    S.DUPLICADO: frozenset(),  # status terminal sem transição prevista
}


def transicao_valida(atual: S, novo: S) -> bool:
    """Retorna True se a transição de `atual` para `novo` é permitida."""
    if atual == novo:
        return False  # sem mudança — o router trata como 409
    destinos = TRANSICOES_VALIDAS.get(atual, frozenset())
    return novo in destinos


def validar_transicao(atual: S, novo: S) -> None:
    """
    Lança ValueError se a transição não for permitida.

    O router converte o ValueError em HTTPException 422.
    """
    if not transicao_valida(atual, novo):
        raise ValueError(
            f"Transição inválida: '{atual.label}' → '{novo.label}'. "
            f"A partir de '{atual.label}', os destinos válidos são: "
            f"{', '.join(sorted(s.label for s in TRANSICOES_VALIDAS.get(atual, frozenset()))) or 'nenhum'}."
        )

