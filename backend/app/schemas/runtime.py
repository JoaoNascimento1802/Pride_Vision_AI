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
