# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
remediation.py — Schemas para comentários e evidências de remediação.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(..., max_length=5000, description="Conteúdo do comentário")


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vulnerability_id: int
    author_id: int | None
    author_name: str | None = None
    content: str
    created_at: datetime


class EvidenceCreate(BaseModel):
    evidence_type: str = Field(default="other", max_length=50, description="Tipo de evidência (commit, pr, scan, description, other)")
    description: str = Field(..., max_length=2000, description="Descrição da evidência")
    reference: str | None = Field(default=None, max_length=500, description="URL ou referência externa")


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vulnerability_id: int
    author_id: int | None
    author_name: str | None = None
    evidence_type: str
    description: str
    reference: str | None
    created_at: datetime

