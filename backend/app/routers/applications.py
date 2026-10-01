"""
applications.py — Inventário de aplicações.

O inventário é o primeiro dos quatro pilares de ASPM da especificação. É aqui
que entram os dados de contexto (ambiente, exposição, importância) que o motor
de risco usa depois para priorizar.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.database import get_db
from app.models import Application, Risco, StatusVulnerabilidade, Vulnerability
from app.schemas import (
    ApplicationCreate,
    ApplicationListItem,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.services import reclassificar_aplicacao

router = APIRouter(
    prefix="/api/aplicacoes",
    tags=["Aplicações"],
    dependencies=[Depends(usuario_atual)],
)

# Status que ainda demandam trabalho da equipe
_STATUS_ABERTOS = (
    StatusVulnerabilidade.NOVA,
    StatusVulnerabilidade.EM_ANALISE,
    StatusVulnerabilidade.EM_CORRECAO,
)


def _buscar_ou_404(db: Session, aplicacao_id: int) -> Application:
    aplicacao = db.get(Application, aplicacao_id)
    if aplicacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Aplicação não encontrada."
        )
    return aplicacao


@router.get("", response_model=list[ApplicationListItem])
def listar(
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> list[ApplicationListItem]:
    """
    Lista as aplicações com os contadores da tela de aplicações.

    Os totais vêm de uma única consulta agregada em vez de uma por aplicação,
    para a tela não degradar conforme o inventário cresce.
    """
    aplicacoes = db.scalars(select(Application).order_by(Application.nome)).all()

    total_por_app = {
        linha[0]: linha[1]
        for linha in db.execute(
            select(Vulnerability.aplicacao_id, func.count(Vulnerability.id)).group_by(
                Vulnerability.aplicacao_id
            )
        ).all()
    }

    criticas_por_app = {
        linha[0]: linha[1]
        for linha in db.execute(
            select(Vulnerability.aplicacao_id, func.count(Vulnerability.id))
            .where(Vulnerability.risco == Risco.CRITICO)
            .group_by(Vulnerability.aplicacao_id)
        ).all()
    }

    abertas_por_app = {
        linha[0]: linha[1]
        for linha in db.execute(
            select(Vulnerability.aplicacao_id, func.count(Vulnerability.id))
            .where(Vulnerability.status.in_(_STATUS_ABERTOS))
            .group_by(Vulnerability.aplicacao_id)
        ).all()
    }

    return [
        ApplicationListItem(
            **ApplicationResponse.model_validate(app).model_dump(),
            total_vulnerabilidades=total_por_app.get(app.id, 0),
            total_criticas=criticas_por_app.get(app.id, 0),
            total_abertas=abertas_por_app.get(app.id, 0),
        )
        for app in aplicacoes
    ]


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def criar(
    dados: ApplicationCreate,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:write")),
) -> Application:
    """Cadastra uma aplicação no inventário."""
    aplicacao = Application(
        nome=dados.nome.strip(),
        responsavel=dados.responsavel.strip(),
        ambiente=dados.ambiente,
        exposicao=dados.exposicao,
        importancia=dados.importancia,
        url=dados.url.strip() if dados.url else None,
    )
    db.add(aplicacao)
    db.commit()
    db.refresh(aplicacao)
    return aplicacao


@router.get("/{aplicacao_id}", response_model=ApplicationResponse)
def obter(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> Application:
    return _buscar_ou_404(db, aplicacao_id)


@router.patch("/{aplicacao_id}", response_model=ApplicationResponse)
def atualizar(
    aplicacao_id: int,
    dados: ApplicationUpdate,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:write")),
) -> Application:
    """
    Edita a aplicação.

    Alterar ambiente, exposição ou importância muda o contexto de negócio, e as
    vulnerabilidades já registradas são reclassificadas na hora — do contrário o
    inventário e a priorização ficariam contando histórias diferentes: a
    aplicação apareceria como de teste enquanto suas vulnerabilidades
    continuariam classificadas como se estivessem em produção.
    """
    aplicacao = _buscar_ou_404(db, aplicacao_id)

    alteracoes = dados.model_dump(exclude_unset=True)
    mudou_contexto = any(campo in alteracoes for campo in ("ambiente", "exposicao", "importancia"))

    for campo, valor in alteracoes.items():
        if isinstance(valor, str):
            valor = valor.strip()
        setattr(aplicacao, campo, valor)

    db.commit()

    if mudou_contexto:
        reclassificar_aplicacao(db, aplicacao)

    db.refresh(aplicacao)
    return aplicacao


@router.delete("/{aplicacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:write")),
) -> None:
    """
    Remove a aplicação e tudo que veio dela.

    Uploads, achados e vulnerabilidades são apagados em cascata: manter
    vulnerabilidades de uma aplicação que saiu do inventário só produziria
    números errados no dashboard.
    """
    aplicacao = _buscar_ou_404(db, aplicacao_id)
    db.delete(aplicacao)
    db.commit()


@router.get("/{aplicacao_id}/resumo", response_model=dict)
def resumo(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> dict[str, object]:
    """Contagem de vulnerabilidades por risco e por status de uma aplicação."""
    _buscar_ou_404(db, aplicacao_id)

    por_risco = {risco.value: 0 for risco in sorted(Risco, key=lambda r: r.ordem)}
    for valor, total in db.execute(
        select(Vulnerability.risco, func.count(Vulnerability.id))
        .where(Vulnerability.aplicacao_id == aplicacao_id)
        .group_by(Vulnerability.risco)
    ).all():
        por_risco[valor.value] = total

    por_status = {s.value: 0 for s in StatusVulnerabilidade}
    for valor, total in db.execute(
        select(Vulnerability.status, func.count(Vulnerability.id))
        .where(Vulnerability.aplicacao_id == aplicacao_id)
        .group_by(Vulnerability.status)
    ).all():
        por_status[valor.value] = total

    return {
        "aplicacao_id": aplicacao_id,
        "por_risco": por_risco,
        "por_status": por_status,
        "total": sum(por_risco.values()),
    }
