from app.models.tenant import Tenant, TenantUser
from app.models.enums import Role

with open('backend/app/routers/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

sso_code = """
from app.models.tenant import Tenant, TenantUser
from app.models.enums import Role

@router.get("/sso/login")
def sso_login(domain: str, db: Session = Depends(get_db)):
    tenant = db.scalar(select(Tenant).where(Tenant.domain == domain))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado para este domínio")
    return {"redirect_url": f"https://sso.provider.com/auth?domain={domain}"}

@router.get("/sso/callback", response_model=TokenResponse)
def sso_callback(email: str, db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)):
    domain = email.split('@')[-1]
    tenant = db.scalar(select(Tenant).where(Tenant.domain == domain))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não configurado")
    
    usuario = _buscar_por_email(db, email)
    if not usuario:
        usuario = User(email=email, nome=email.split('@')[0], senha_hash="SSO_MANAGED")
        db.add(usuario)
        db.flush()
        tu = TenantUser(tenant_id=tenant.id, user_id=usuario.id, role=Role.DEVELOPER)
        db.add(tu)
        
    audit.log_action(
        action=AuditAction.LOGIN_SUCCESS,
        actor_user_id=usuario.id,
        entity_type=EntityType.USER,
        entity_id=str(usuario.id),
        metadata_info={"sso": True, "tenant": tenant.domain}
    )
    db.commit()
    
    return TokenResponse(
        access_token=criar_token(usuario.id, usuario.email),
        usuario=UsuarioResponse.model_validate(usuario),
    )
"""

text += "\n" + sso_code

with open('backend/app/routers/auth.py', 'w', encoding='utf-8') as f:
    f.write(text)
