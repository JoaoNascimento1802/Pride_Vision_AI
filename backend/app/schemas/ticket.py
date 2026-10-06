# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TicketProvider, TicketStatus


class TicketResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: TicketProvider
    external_id: str
    external_key: str | None
    url: str
    title: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    last_synced_at: datetime | None


class TicketCriarRequisicao(BaseModel):
    provider: TicketProvider
