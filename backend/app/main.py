# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
main.py — Aplicação FastAPI.

Monta os routers, configura CORS para o frontend React e cria as tabelas na
inicialização.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app import __version__
from app.config import settings
from app.database import _fabrica_de_sessoes, criar_tabelas
from app.models.enums import (
    Ambiente,
    EnumRotulado,
    Exposicao,
    Importancia,
    Risco,
    StatusVulnerabilidade,
)
from app.routers import (
    applications,
    audit,
    auth,
    ci,
    cspm,
    dashboard,
    integrations,
    observability,
    runtime,
    sboms,
    supply_chain,
    tickets,
    uploads,
    vulnerabilities,
)
from app.services.data_masker import mascarar
from app.services.sla_service import SlaService
from app.telemetry import setup_telemetry, telemetry_middleware

# Motivo pelo qual o banco não pôde ser preparado, ou None quando está tudo bem.
# Fica em módulo porque a rota de saúde precisa lê-lo sem receber a requisição.
_ERRO_BANCO: str | None = None


def _habilitar_saida_utf8() -> None:
    """
    Força stdout/stderr a UTF-8.

    As mensagens de log são em português. No console do Windows (cp1252) os
    acentos sairiam corrompidos, o que atrapalha justamente na hora de ler um
    aviso de configuração.
    """
    for fluxo in (sys.stdout, sys.stderr):
        reconfigure = getattr(fluxo, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):  # pragma: no cover — fluxos exóticos
                pass





async def _sla_scheduler() -> None:
    """Executa a verificação de SLA periodicamente."""
    while True:
        try:
            with _fabrica_de_sessoes()() as db:
                SlaService.check_and_update_slas(db)
        except Exception as e:
            print(f"[ERROR] SLA Scheduler falhou: {e}")
        await asyncio.sleep(60 * 60)  # Roda a cada hora

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:

    """Prepara o banco na subida e avisa sobre configuração faltando."""
    global _ERRO_BANCO

    _habilitar_saida_utf8()
    setup_telemetry()

    # Falhar aqui derrubaria o processo inteiro, e a plataforma responderia o erro
    # genérico do provedor em TODAS as rotas — inclusive nesta, que é justamente a
    # que existe para dizer o que está errado. Registrar e seguir mantém o
    # diagnóstico disponível. Ver AC-ARQ-19.
    try:
        criar_tabelas()
        _ERRO_BANCO = None
        asyncio.create_task(_sla_scheduler())
    except Exception as exc:  # noqa: BLE001 — qualquer falha de banco vira diagnóstico
        _ERRO_BANCO = mascarar(
            f"{type(exc).__name__}: {str(exc).splitlines()[0]}",
            settings.PRIDE_INTERNAL_NAMES,
        )
        print(
            f"[ERROR] Banco indisponível na inicialização: {_ERRO_BANCO} "
            "As rotas de dados vão falhar; consulte GET /api/saude.",
            file=sys.stderr,
        )

    if not settings.SECRET_KEY_DEFINIDA:
        print(
            "[WARN] SECRET_KEY não definida — uma chave aleatória foi gerada. "
            "Os tokens deixarão de valer a cada reinício. "
            "Defina SECRET_KEY no .env antes de publicar.",
            file=sys.stderr,
        )
    elif settings.secret_key_fraca:
        print(
            f"[WARN] SECRET_KEY tem menos de {settings.SECRET_KEY_MIN_BYTES} bytes. "
            "Quem descobrir a chave consegue forjar o token de qualquer usuário. "
            'Gere uma chave forte com: python -c "import secrets; '
            'print(secrets.token_urlsafe(32))"',
            file=sys.stderr,
        )

    if not settings.ia_configurada:
        print(
            f"[INFO] Sem chave de IA para o provedor '{settings.AI_DEFAULT_PROVIDER}'. "
            "A plataforma funciona normalmente; apenas as explicações geradas por "
            "IA ficarão indisponíveis.",
            file=sys.stderr,
        )

    yield


app = FastAPI(
    title="PRIDE Vision AI",
    description=(
        "Plataforma simplificada de ASPM. Centraliza achados do Semgrep e do "
        "Nuclei, correlaciona os resultados, prioriza pelo risco técnico somado "
        "ao contexto do negócio e acompanha o ciclo de correção."
    ),
    version=__version__,
    lifespan=lifespan,
)

# O React roda em outra origem durante o desenvolvimento (Vite na 5173) e em
# outro domínio depois de publicado, então o CORS precisa liberar explicitamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(uploads.router)
app.include_router(vulnerabilities.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(sboms.router)
app.include_router(tickets.router)
app.include_router(ci.router)
app.include_router(integrations.router)

app.include_router(supply_chain.router)
app.include_router(runtime.router)
app.include_router(cspm.router)
app.include_router(observability.router)

app.add_middleware(BaseHTTPMiddleware, dispatch=telemetry_middleware)


@app.get("/api/saude", tags=["Infraestrutura"])
def saude() -> dict[str, object]:
    """
    Verificação de saúde.

    A hospedagem usa esta rota para saber se o processo subiu, e ela também
    serve para conferir rapidamente como a IA está configurada no ambiente.

    O modelo aparece aqui porque descobrir qual está em uso é a parte difícil de
    diagnosticar quando um provedor aposenta um nome: a API passa a responder
    "modelo inválido" com uma chave perfeitamente válida.
    """
    return {
        "status": "ok" if _ERRO_BANCO is None else "degradado",
        "versao": __version__,
        "banco": "ok" if _ERRO_BANCO is None else _ERRO_BANCO,
        "ia_configurada": settings.ia_configurada,
        "provedor_ia": settings.AI_DEFAULT_PROVIDER,
        "modelo_ia": settings.modelo_ia_previsto,
    }


@app.get("/api/opcoes", tags=["Infraestrutura"])
def opcoes() -> dict[str, list[dict[str, str]]]:
    """
    Vocabulário controlado do sistema, com slug e rótulo.

    A interface usa esta rota para montar os campos de seleção e as legendas dos
    gráficos, em vez de manter uma cópia das listas que sairia de sincronia com
    o backend.
    """

    def opcoes_de(enum_cls: type[EnumRotulado]) -> list[dict[str, str]]:
        return [{"valor": m.value, "label": m.label} for m in enum_cls]

    return {
        "ambientes": opcoes_de(Ambiente),
        "exposicoes": opcoes_de(Exposicao),
        "importancias": opcoes_de(Importancia),
        "riscos": [
            {"valor": r.value, "label": r.label} for r in sorted(Risco, key=lambda r: r.ordem)
        ],
        "status": opcoes_de(StatusVulnerabilidade),
    }
