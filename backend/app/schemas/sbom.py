from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SbomComponentResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    versao: str | None
    ecossistema: str | None
    purl: str | None
    licenca: str | None
    cve_relacionada: str | None


class SbomComponentDetalhe(SbomComponentResumo):
    tipo_componente: str | None
    cpe: str | None
    fornecedor: str | None
    hashes: str | None


class SbomResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    formato: str
    versao_formato: str | None
    nome_arquivo: str
    criado_em: datetime


class SbomDetalhe(SbomResumo):
    tamanho_bytes: int
    serial_number: str | None
    generated_at: datetime | None
    componentes: list[SbomComponentResumo]
