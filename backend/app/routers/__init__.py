"""routers — Camada HTTP. Traduz requisições para os serviços e de volta."""

from app.routers import applications, auth, dashboard, uploads, vulnerabilities

__all__ = ["applications", "auth", "dashboard", "uploads", "vulnerabilities"]
