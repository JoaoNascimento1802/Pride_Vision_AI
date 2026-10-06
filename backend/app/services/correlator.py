# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
correlator.py — Correlação determinística dos achados.

Migrado da POC. Agrupa por tipo de vulnerabilidade e compatibilidade de
endpoint. Sem heurística, sem aprendizado de máquina, sem pontuação: apenas as
regras explicáveis de `normalizer.endpoints_compativeis`.
"""

from __future__ import annotations

from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado
from app.services.normalizer import endpoints_compativeis


def _endpoint_canonico(endpoints: list[str]) -> str:
    """
    Escolhe o endpoint que melhor representa o grupo.

    Endpoints em formato de rota (começando com "/") têm preferência sobre
    caminhos de arquivo, porque é a rota que interessa exibir. Entre os
    candidatos vence o mais curto, com desempate alfabético — assim o resultado
    nunca depende da ordem de entrada.
    """
    rotas = [e for e in endpoints if e.startswith("/")]
    candidatos = rotas or endpoints
    return min(candidatos, key=lambda e: (len(e), e))


def _componentes_conexas(achados: list[AchadoNormalizado]) -> list[list[AchadoNormalizado]]:
    """
    Divide os achados em grupos ligados por compatibilidade de endpoint.

    Usa união-busca sobre todos os pares. As componentes conexas resultantes são
    as mesmas independentemente da ordem em que os achados chegam, o que mantém
    a correlação confluente.
    """
    pai = list(range(len(achados)))

    def raiz(i: int) -> int:
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    def unir(i: int, j: int) -> None:
        ri, rj = raiz(i), raiz(j)
        if ri != rj:
            pai[max(ri, rj)] = min(ri, rj)

    for i in range(len(achados)):
        for j in range(i + 1, len(achados)):
            if endpoints_compativeis(achados[i].endpoint, achados[j].endpoint):
                unir(i, j)

    componentes: dict[int, list[AchadoNormalizado]] = {}
    for indice, achado in enumerate(achados):
        componentes.setdefault(raiz(indice), []).append(achado)

    return list(componentes.values())


def correlacionar(achados: list[AchadoNormalizado]) -> list[GrupoCorrelacionado]:
    """
    Agrupa achados em vulnerabilidades correlacionadas.

    Regras:
    - O tipo da vulnerabilidade precisa ser igual.
    - O endpoint precisa ser igual ou compatível.
    - Cada achado pertence a exatamente um grupo.
    - A ordem da entrada não altera os grupos formados.
    """
    por_tipo: dict[str, list[AchadoNormalizado]] = {}
    for achado in achados:
        por_tipo.setdefault(achado.tipo_vuln, []).append(achado)

    grupos: list[GrupoCorrelacionado] = []
    for tipo_vuln, do_tipo in por_tipo.items():
        for componente in _componentes_conexas(do_tipo):
            grupos.append(
                GrupoCorrelacionado(
                    tipo_vuln=tipo_vuln,
                    endpoint=_endpoint_canonico([a.endpoint for a in componente]),
                    achados=componente,
                )
            )

    return grupos
