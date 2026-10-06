# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/auth/dependencies.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """from fastapi import Depends, HTTPException, status, Header
from app.database import current_tenant_id
from app.models.tenant import TenantUser

def usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    x_tenant_id: int | None = Header(None, alias="X-Tenant-ID"),
) -> User:
    usuario_id = ler_token(token)
    if usuario_id is None:
        raise CREDENCIAIS_INVALIDAS

    usuario = db.get(User, usuario_id)
    if usuario is None:
        raise CREDENCIAIS_INVALIDAS

    # Se a rota exige tenant (ou passou o tenant), valida
    if x_tenant_id is not None:
        tu = db.query(TenantUser).filter_by(tenant_id=x_tenant_id, user_id=usuario.id).first()
        if tu is None:
            raise HTTPException(status_code=403, detail="Acesso negado a este Tenant")
        current_tenant_id.set(x_tenant_id)
        # Override a role global com a role do tenant temporariamente na memoria
        usuario.role = tu.role
    else:
        # Backward compatibility for endpoints not passing Tenant-ID yet
        current_tenant_id.set(1)
        
    return usuario
"""

import re
text = re.sub(r'def usuario_atual\([\s\S]*?return usuario', replacement, text)

# fix imports
if 'Header' not in text:
    text = text.replace('from fastapi import Depends, HTTPException, status', 'from fastapi import Depends, HTTPException, status, Header')

with open('backend/app/auth/dependencies.py', 'w', encoding='utf-8') as f:
    f.write(text)
