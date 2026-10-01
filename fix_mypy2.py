with open('backend/app/database.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('def _add_tenant_filter(execute_state):', 'from typing import Any\ndef _add_tenant_filter(execute_state: Any) -> None:')
text = text.replace('if hasattr(cls, "tenant_id") else True,', 'if hasattr(cls, "tenant_id") else True,  # type: ignore')

with open('backend/app/database.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('backend/app/auth/dependencies.py', 'r', encoding='utf-8') as f:
    text2 = f.read()
text2 = text2.replace('usuario.current_role = tu.role', 'setattr(usuario, "current_role", tu.role)')
with open('backend/app/auth/dependencies.py', 'w', encoding='utf-8') as f:
    f.write(text2)

with open('backend/app/routers/auth.py', 'r', encoding='utf-8') as f:
    text3 = f.read()
text3 = text3.replace('def sso_login(domain: str, db: Session = Depends(get_db)):', 'def sso_login(domain: str, db: Session = Depends(get_db)) -> dict[str, str]:')
text3 = text3.replace('def sso_callback(email: str, db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)):', 'def sso_callback(email: str, db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> TokenResponse:')
with open('backend/app/routers/auth.py', 'w', encoding='utf-8') as f:
    f.write(text3)
