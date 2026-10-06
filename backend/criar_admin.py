# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import obter_engine, get_db, Base
from app.models.user import User
from app.models.tenant import Tenant, TenantUser
from app.models.enums import Role
from app.auth.security import gerar_hash_senha

engine = obter_engine()
Base.metadata.create_all(bind=engine)

db_gen = get_db()
db = next(db_gen)

try:
    tenant = db.query(Tenant).filter_by(name="Default Workspace").first()
    if not tenant:
        tenant = Tenant(name="Default Workspace", domain="pride.local")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    email = "admin@pride.com"
    admin = db.query(User).filter_by(email=email).first()
    if not admin:
        admin = User(email=email, nome="Administrador Supremo", senha_hash=gerar_hash_senha("admin"))
        db.add(admin)
        db.commit()
        db.refresh(admin)

    admin.role = Role.ADMIN
    db.commit()

    tu = db.query(TenantUser).filter_by(tenant_id=tenant.id, user_id=admin.id).first()
    if not tu:
        tu = TenantUser(tenant_id=tenant.id, user_id=admin.id, role=Role.ADMIN)
        db.add(tu)
        db.commit()

    print(f'Usuário criado com sucesso: {email} / senha: admin')
finally:
    try:
        next(db_gen)
    except StopIteration:
        pass