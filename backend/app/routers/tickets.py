# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.database import get_db
from app.models.enums import AuditAction, EntityType
from app.models.ticket import Ticket
from app.models.vulnerability import Vulnerability
from app.schemas.ticket import TicketCriarRequisicao, TicketResumo
from app.services.audit import AuditService, get_audit_service
from app.services.ticketing import criar_ticket, sincronizar_ticket

router = APIRouter(
    prefix="/api/vulnerabilidades/{vulnerabilidade_id}/tickets",
    tags=["Tickets"],
    dependencies=[Depends(usuario_atual)],
)


@router.post("", response_model=TicketResumo, status_code=status.HTTP_201_CREATED)
def criar(
    vulnerabilidade_id: int,
    req: TicketCriarRequisicao,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("ticket:create")),
    audit: AuditService = Depends(get_audit_service),
) -> Any:
    vuln = db.get(Vulnerability, vulnerabilidade_id)
    if not vuln:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Vulnerabilidade não encontrada.")
    try:
        ticket = criar_ticket(db, vuln, req.provider, usuario.id)
        audit.log_action(
            action=AuditAction.CREATE_TICKET,
            actor_user_id=usuario.id,
            entity_type=EntityType.TICKET,
            entity_id=str(ticket.id),
            new_value={"provider": req.provider.value, "vulnerability_id": vulnerabilidade_id}
        )
        db.commit()
        return ticket
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{ticket_id}/sync", response_model=TicketResumo)
def sincronizar(
    vulnerabilidade_id: int,
    ticket_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("ticket:sync")),
    audit: AuditService = Depends(get_audit_service),
) -> Any:
    ticket = db.get(Ticket, ticket_id)
    if not ticket or ticket.vulnerabilidade_id != vulnerabilidade_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ticket não encontrado.")

    try:
        ticket = sincronizar_ticket(db, ticket, usuario.id)
        audit.log_action(
            action=AuditAction.SYNC_TICKET,
            actor_user_id=usuario.id,
            entity_type=EntityType.TICKET,
            entity_id=str(ticket.id),
            new_value={"status": ticket.status.value} if ticket.status else {}
        )
        db.commit()
        return ticket
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
