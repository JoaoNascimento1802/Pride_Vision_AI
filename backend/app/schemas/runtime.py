# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import datetime

from pydantic import BaseModel, Field


class FalcoOutputFields(BaseModel):
    container_id: str | None = Field(default=None, alias="container.id")
    proc_name: str | None = Field(default=None, alias="proc.name")
    evt_type: str | None = Field(default=None, alias="evt.type")

    model_config = {"extra": "allow", "populate_by_name": True}

class FalcoEvent(BaseModel):
    rule: str
    priority: str
    output: str
    time: datetime
    output_fields: FalcoOutputFields = Field(default_factory=FalcoOutputFields)

class RuntimeIngestionResponse(BaseModel):
    status: str
    events_processed: int
    vulnerability_id: int | None = None

class RuntimeEventResponse(BaseModel):
    id: int
    aplicacao_id: int | None
    container_id: str | None
    process_name: str | None
    syscall: str | None
    rule_name: str | None = Field(default=None, alias="regra_id")
    severidade: str
    mensagem: str | None
    hit_count: int
    last_seen_at: datetime
    vulnerabilidade_id: int | None

    model_config = {"from_attributes": True, "populate_by_name": True}
