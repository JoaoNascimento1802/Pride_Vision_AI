# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
services — Regras de negócio.

`normalizer`, `correlator`, `data_masker` e `risk_engine` são funções puras: não
tocam banco nem rede, o que permite testá-las isoladamente e auditar a
classificação de risco. `ingestion` é a única camada que junta essas regras com
persistência.
"""

from app.services.correlator import correlacionar
from app.services.data_masker import mascarar
from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado, ResultadoParse
from app.services.ingestion import (
    ResultadoIngestao,
    contexto_de,
    ingerir_relatorio,
    reclassificar_aplicacao,
    recorrelacionar,
)
from app.services.normalizer import (
    endpoints_compativeis,
    ler_nuclei,
    ler_semgrep,
    normalizar_endpoint,
    normalizar_tipo,
)
from app.services.risk_engine import ContextoAplicacao, ResultadoRisco, classificar

__all__ = [
    "AchadoNormalizado",
    "ContextoAplicacao",
    "GrupoCorrelacionado",
    "ResultadoIngestao",
    "ResultadoParse",
    "ResultadoRisco",
    "classificar",
    "contexto_de",
    "correlacionar",
    "endpoints_compativeis",
    "ingerir_relatorio",
    "ler_nuclei",
    "ler_semgrep",
    "mascarar",
    "normalizar_endpoint",
    "normalizar_tipo",
    "reclassificar_aplicacao",
    "recorrelacionar",
]
