import uuid
from typing import Any

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit import AuditLog
from app.models.enums import AuditAction, EntityType

SENSITIVE_KEYS = {
    "password", "token", "access_token", "refresh_token", "authorization",
    "api_key", "secret", "secret_key", "client_secret", "private_key",
    "jwt", "credential"
}

def sanitize_data(data: Any) -> Any:
    """Recursively masks sensitive keys in dicts and lists."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sensitive in k.lower() for sensitive in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data


class AuditService:
    def __init__(self, db: Session, request: Request | None = None, request_id: str | None = None):
        self.db = db
        self.request = request
        self.request_id = request_id

        # Extract IP and User Agent if request is provided
        self.ip_address = None
        self.user_agent = None
        if self.request:
            if hasattr(self.request, "client") and self.request.client:
                self.ip_address = self.request.client.host
            self.user_agent = self.request.headers.get("User-Agent")

    def log_action(
        self,
        action: AuditAction,
        actor_user_id: int | None = None,
        entity_type: EntityType | None = None,
        entity_id: str | None = None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        metadata_info: dict[str, Any] | None = None,
    ) -> AuditLog:
        """
        Creates and persists an audit log entry in the same session.
        Sensitive keys are recursively masked.
        """
        log_entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=sanitize_data(old_value) if old_value else None,
            new_value=sanitize_data(new_value) if new_value else None,
            metadata_info=sanitize_data(metadata_info) if metadata_info else None,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            request_id=self.request_id,
        )
        self.db.add(log_entry)
        self.db.flush()
        return log_entry


def get_audit_service(request: Request, db: Session = Depends(get_db)) -> AuditService:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return AuditService(db=db, request=request, request_id=request_id)
