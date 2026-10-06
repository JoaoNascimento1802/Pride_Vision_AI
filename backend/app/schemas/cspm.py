# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿from typing import Literal

from pydantic import BaseModel


class CSPMEvent(BaseModel):
    """Payload de entrada de um evento de Cloud Posture (ex: AWS Security Hub / Prowler webhook)."""
    provider: Literal["aws", "gcp", "azure"]
    account_id: str
    resource_id: str
    resource_type: str = "unknown"
    region: str
    compliance_framework: str | None = None
    compliance_control: str | None = None
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    title: str
    description: str
