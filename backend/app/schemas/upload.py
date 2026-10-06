# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
upload.py — Schemas do envio de relatórios.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.models.enums import Ferramenta


class ResultadoUploadResponse(BaseModel):
    """
    O que aconteceu com o relatório enviado.

    Traz os avisos de entradas descartadas para o usuário não achar que o
    arquivo foi aceito por inteiro quando parte dele estava malformada.
    """

    upload_id: int
    ferramenta: Ferramenta
    ferramenta_label: str

    achados_lidos: int
    achados_ignorados: int
    avisos: list[str]

    vulnerabilidades_totais: int
    vulnerabilidades_novas: int
    vulnerabilidades_atualizadas: int


class UploadResumo(BaseModel):
    """Relatório em vigor para uma aplicação."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ferramenta: Ferramenta
    nome_arquivo: str
    tamanho_bytes: int
    total_achados: int
    total_ignorados: int
    criado_em: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ferramenta_label(self) -> str:
        return self.ferramenta.label
