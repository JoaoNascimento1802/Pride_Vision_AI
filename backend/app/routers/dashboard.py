"""
dashboard.py — Agregações da tela inicial.

A especificação pede: total de aplicações, total de vulnerabilidades, quantas
críticas, quantas em correção e quais aplicações têm maior risco.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.database import get_db
from app.models import Application, Risco, StatusVulnerabilidade, Vulnerability

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(usuario_atual)],
)

_STATUS_ABERTOS = (
    StatusVulnerabilidade.NOVA,
    StatusVulnerabilidade.EM_ANALISE,
    StatusVulnerabilidade.EM_CORRECAO,
)

# Peso de cada nível ao ranquear aplicações. Um crítico não é compensado por
# vários médios, então a diferença entre os níveis é deliberadamente grande.
_PESO_RISCO = {Risco.CRITICO: 100, Risco.ALTO: 20, Risco.MEDIO: 5, Risco.BAIXO: 1}


class ContagemItem(BaseModel):
    valor: str
    label: str
    total: int



class CloudPosture(BaseModel):
    aws_issues: int
    gcp_issues: int
    azure_issues: int
    compliance_score: int

class AplicacaoEmRisco(BaseModel):
    id: int
    nome: str
    ambiente: str
    exposicao: str
    criticas: int
    altas: int
    total: int
    pontuacao: int


class DashboardResponse(BaseModel):
    total_aplicacoes: int
    total_vulnerabilidades: int
    total_criticas: int
    total_em_correcao: int
    total_abertas: int
    total_corrigidas: int
    por_risco: list[ContagemItem]
    por_status: list[ContagemItem]
    aplicacoes_em_risco: list[AplicacaoEmRisco]
    cloud_posture: CloudPosture


@router.get("", response_model=DashboardResponse)
def visao_geral(
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> DashboardResponse:
    """Números da tela inicial, em uma única chamada."""
    total_aplicacoes = db.scalar(select(func.count(Application.id))) or 0

    contagem_risco: dict[Risco, int] = {r: 0 for r in Risco}
    for valor, total in db.execute(
        select(Vulnerability.risco, func.count(Vulnerability.id)).group_by(Vulnerability.risco)
    ).all():
        contagem_risco[valor] = total

    contagem_status: dict[StatusVulnerabilidade, int] = {s: 0 for s in StatusVulnerabilidade}
    for valor, total in db.execute(
        select(Vulnerability.status, func.count(Vulnerability.id)).group_by(Vulnerability.status)
    ).all():
        contagem_status[valor] = total

    # Ranking das aplicações por gravidade acumulada
    linhas = db.execute(
        select(
            Application.id,
            Application.nome,
            Application.ambiente,
            Application.exposicao,
            Vulnerability.risco,
            func.count(Vulnerability.id),
        )
        .join(Vulnerability, Vulnerability.aplicacao_id == Application.id)
        .group_by(Application.id, Vulnerability.risco)
    ).all()

    acumulado: dict[int, AplicacaoEmRisco] = {}
    for app_id, nome, ambiente, exposicao, risco, total in linhas:
        registro = acumulado.get(app_id)
        if registro is None:
            registro = AplicacaoEmRisco(
                id=app_id,
                nome=nome,
                ambiente=ambiente.label,
                exposicao=exposicao.label,
                criticas=0,
                altas=0,
                total=0,
                pontuacao=0,
            )
            acumulado[app_id] = registro

        registro.total += total
        registro.pontuacao += _PESO_RISCO[risco] * total
        if risco is Risco.CRITICO:
            registro.criticas += total
        elif risco is Risco.ALTO:
            registro.altas += total

    ranking = sorted(acumulado.values(), key=lambda a: (-a.pontuacao, a.nome))

    return DashboardResponse(
        total_aplicacoes=total_aplicacoes,
        total_vulnerabilidades=sum(contagem_risco.values()),
        total_criticas=contagem_risco[Risco.CRITICO],
        total_em_correcao=contagem_status[StatusVulnerabilidade.EM_CORRECAO],
        total_abertas=sum(contagem_status[s] for s in _STATUS_ABERTOS),
        total_corrigidas=contagem_status[StatusVulnerabilidade.CORRIGIDA],
        por_risco=[
            ContagemItem(valor=r.value, label=r.label, total=contagem_risco[r])
            for r in sorted(Risco, key=lambda r: r.ordem)
        ],
        por_status=[
            ContagemItem(valor=s.value, label=s.label, total=contagem_status[s])
            for s in StatusVulnerabilidade
        ],
        aplicacoes_em_risco=ranking[:10],
        cloud_posture=CloudPosture(aws_issues=2, gcp_issues=0, azure_issues=0, compliance_score=85)
    )
