# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
data_masker.py — Mascaramento de dados sensíveis antes de qualquer envio à IA.

Migrado da POC sem alteração de comportamento. Os padrões são compilados uma vez
na importação e aplicados em ordem — os primeiros têm precedência quando dois
casam o mesmo trecho.

A função é pura: não altera estado nem depende de nada externo.
"""

from __future__ import annotations

import re

_PADROES: list[tuple[re.Pattern[str], str]] = [
    # JWT — precisa vir antes da regra genérica de Bearer, senão o Bearer casa
    # primeiro e o token fica só parcialmente mascarado
    (
        re.compile(r"eyJ[\w\-]+\.eyJ[\w\-]+\.[\w\-]+"),
        "[TOKEN_MASCARADO]",
    ),
    # Cabeçalho Authorization
    (
        re.compile(r"Bearer\s+[\w\-\.]+", re.IGNORECASE),
        "[TOKEN_MASCARADO]",
    ),
    # Chaves de API atribuídas a uma variável
    (
        re.compile(
            r'(?:api_?key|apikey|key)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{20,64})["\']?',
            re.IGNORECASE,
        ),
        "[API_KEY_MASCARADO]",
    ),
    # Senhas atribuídas a uma variável
    (
        re.compile(
            r'(?:password|passwd|pwd|senha)\s*[=:]\s*["\']?([^\s"\']{1,128})["\']?',
            re.IGNORECASE,
        ),
        "[SENHA_MASCARADA]",
    ),
    # IPv4
    (
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "[IP_MASCARADO]",
    ),
    # IPv6 (simplificado: grupos hexadecimais separados por dois-pontos)
    (
        re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b"),
        "[IP_MASCARADO]",
    ),
    # E-mails
    (
        re.compile(r"\b[\w.+\-]+@[\w.\-]+\.[a-zA-Z]{2,}\b"),
        "[EMAIL_MASCARADO]",
    ),
]


def mascarar(texto: str, nomes_internos: list[str] | None = None) -> str:
    """
    Substitui dados sensíveis por marcadores.

    Aplica todos os padrões e depois troca literalmente cada nome interno
    informado. IPs e e-mails seguem formatos reconhecíveis por expressão
    regular, mas nomes como "servidor-prod-01" não têm como ser adivinhados —
    por isso precisam ser configurados.

    Args:
        texto: conteúdo a sanitizar.
        nomes_internos: nomes de sistemas ou usuários internos a mascarar.

    Returns:
        Cópia sanitizada do texto.
    """
    resultado = texto
    for padrao, marcador in _PADROES:
        resultado = padrao.sub(marcador, resultado)

    for nome in nomes_internos or []:
        if nome:
            resultado = resultado.replace(nome, "[NOME_MASCARADO]")

    return resultado
