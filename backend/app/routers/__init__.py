# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""routers — Camada HTTP. Traduz requisições para os serviços e de volta."""

from app.routers import applications, auth, dashboard, uploads, vulnerabilities

__all__ = ["applications", "auth", "dashboard", "uploads", "vulnerabilities"]
