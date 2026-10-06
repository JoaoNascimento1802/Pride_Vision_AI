# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""schemas — Contratos de entrada e saída da API (Pydantic)."""

from app.schemas.application import (
    ApplicationCreate,
    ApplicationListItem,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.schemas.auth import RegistroRequest, TokenResponse, UsuarioResponse
from app.schemas.upload import ResultadoUploadResponse, UploadResumo
from app.schemas.vulnerability import (
    AchadoResponse,
    AnaliseIAResponse,
    HistoricoItem,
    MudancaStatusRequest,
    VulnerabilidadeDetalhe,
    VulnerabilidadeListItem,
)

__all__ = [
    "AchadoResponse",
    "AnaliseIAResponse",
    "ApplicationCreate",
    "ApplicationListItem",
    "ApplicationResponse",
    "ApplicationUpdate",
    "HistoricoItem",
    "MudancaStatusRequest",
    "RegistroRequest",
    "ResultadoUploadResponse",
    "TokenResponse",
    "UploadResumo",
    "UsuarioResponse",
    "VulnerabilidadeDetalhe",
    "VulnerabilidadeListItem",
]

# Export cspm if needed
