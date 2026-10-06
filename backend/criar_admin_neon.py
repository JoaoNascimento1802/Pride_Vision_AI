# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Tenant, User, TenantUser, Role
from app.auth.security import gerar_hash_senha

engine = create_engine(os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql+psycopg://'))
with Session(engine) as db:
    tenant1 = Tenant(name="Tenant 1", domain="tenant1")
    tenant2 = Tenant(name="Tenant 2", domain="tenant2")
    db.add_all([tenant1, tenant2])
    db.commit()

    admin = User(email="admin@pride.com", nome="Admin", senha_hash=gerar_hash_senha("admin"), role=Role.ADMIN)
    db.add(admin)
    db.commit()

    tu = TenantUser(tenant_id=tenant2.id, user_id=admin.id, role=Role.ADMIN)
    db.add(tu)
    db.commit()
    print("Admin criado!")