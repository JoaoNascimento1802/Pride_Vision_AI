from fastapi import APIRouter, Depends, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.dependencies import usuario_atual
from app.database import get_db
from app.models.enums import Role
from app.models.user import User

router = APIRouter(tags=["Observability"])



@router.get("/metrics")
def get_metrics(usuario: User = Depends(usuario_atual)) -> Response:
    '''Expõe métricas no formato Prometheus. Apenas ADMIN.'''
    if usuario.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

@router.get("/api/health")
def deep_health_check(response: Response, db: Session = Depends(get_db)) -> dict[str, object]:
    '''Deep Health Check da plataforma.'''
    db_status = "up"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if db_status == "up" else "error",
        "database": db_status,
        "services": {
            "jira": "up",
            "genai": "up"
        }
    }
