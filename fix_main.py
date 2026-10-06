# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

# imports
imports = """
from app.routers import (
    applications,
    audit,
    auth,
    ci,
    cspm,
    dashboard,
    integrations,
    runtime,
    sboms,
    supply_chain,
    tickets,
    uploads,
    vulnerabilities,
    observability,
)
from app.telemetry import setup_telemetry, telemetry_middleware
from starlette.middleware.base import BaseHTTPMiddleware
"""

# Replace imports
text = text.replace("""from app.routers import (
    applications,
    audit,
    auth,
    ci,
    cspm,
    dashboard,
    integrations,
    runtime,
    sboms,
    supply_chain,
    tickets,
    uploads,
    vulnerabilities,
)""", imports)

# Setup telemetry on lifespan
lifespan_old = """
    _habilitar_saida_utf8()

    # Falhar aqui derrubaria o processo inteiro
"""
lifespan_new = """
    _habilitar_saida_utf8()
    setup_telemetry()

    # Falhar aqui derrubaria o processo inteiro
"""
text = text.replace(lifespan_old, lifespan_new)

# Add middleware and router
router_old = """
app.include_router(cspm.router)
# app.include_router(api_security.router)
"""

router_new = """
app.include_router(cspm.router)
app.include_router(observability.router)

app.add_middleware(BaseHTTPMiddleware, dispatch=telemetry_middleware)
"""
text = text.replace(router_old, router_new)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)

