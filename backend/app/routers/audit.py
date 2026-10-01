from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.auth.rbac import Permission
from app.database import get_db
from app.models.audit import AuditLog
from app.models.enums import AuditAction, EntityType
from app.models.user import User
from app.schemas.audit import AuditLogResponse, PaginatedAuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["Auditoria"])


@router.get("", response_model=PaginatedAuditLogResponse, dependencies=[Depends(RequirePermission(Permission.AUDIT_READ))])
def listar_auditoria(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    actor_user_id: int | None = None,
    action: AuditAction | None = None,
    entity_type: EntityType | None = None,
    entity_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(usuario_atual),
) -> PaginatedAuditLogResponse:
    query = db.query(AuditLog)

    if actor_user_id:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)

    total = query.count()
    # Order by newest first
    query = query.order_by(AuditLog.criado_em.desc())
    items = query.offset(skip).limit(limit).all()

    return PaginatedAuditLogResponse(items=[
        AuditLogResponse.model_validate(item) for item in items
    ], total=total)
