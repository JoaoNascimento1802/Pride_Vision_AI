# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import AuditAction, EntityType


class AuditLogResponse(BaseModel):
    id: int
    actor_user_id: int | None
    action: AuditAction
    entity_type: EntityType | None
    entity_id: str | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    metadata_info: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int

