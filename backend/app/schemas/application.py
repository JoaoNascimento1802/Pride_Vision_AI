"""
application.py — Schemas do inventário de aplicações.

As respostas trazem o slug (`producao`) e o rótulo acentuado (`Produção`) lado a
lado. O slug é o que a interface usa em filtros e comparações; o rótulo é o que
ela exibe, sem precisar manter uma tabela de tradução própria.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.enums import Ambiente, Exposicao, Importancia


class ApplicationCreate(BaseModel):
    """Cadastro de uma aplicação no inventário."""

    nome: str = Field(min_length=2, max_length=160)
    responsavel: str = Field(min_length=2, max_length=160)
    ambiente: Ambiente
    exposicao: Exposicao
    importancia: Importancia
    url: str | None = Field(default=None, max_length=500)


class ApplicationUpdate(BaseModel):
    """
    Edição parcial: só os campos enviados são alterados.

    Mudar ambiente, exposição ou importância altera o contexto de negócio e,
    portanto, o risco das vulnerabilidades já registradas — a rota cuida de
    reclassificá-las.
    """

    nome: str | None = Field(default=None, min_length=2, max_length=160)
    responsavel: str | None = Field(default=None, min_length=2, max_length=160)
    ambiente: Ambiente | None = None
    exposicao: Exposicao | None = None
    importancia: Importancia | None = None
    url: str | None = Field(default=None, max_length=500)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    responsavel: str
    url: str | None
    ambiente: Ambiente
    exposicao: Exposicao
    importancia: Importancia
    criado_em: datetime
    atualizado_em: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ambiente_label(self) -> str:
        return self.ambiente.label

    @computed_field  # type: ignore[prop-decorator]
    @property
    def exposicao_label(self) -> str:
        return self.exposicao.label

    @computed_field  # type: ignore[prop-decorator]
    @property
    def importancia_label(self) -> str:
        return self.importancia.label


class ApplicationListItem(ApplicationResponse):
    """
    Item da tela de aplicações.

    Acrescenta os contadores que a especificação pede naquela lista. São
    preenchidos pela rota, não pelo ORM, para evitar uma consulta por linha.
    """

    total_vulnerabilidades: int = 0
    total_criticas: int = 0
    total_abertas: int = 0
