# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import sys

with open('backend/app/routers/supply_chain.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from app.models.audit import AuditAction', 'from app.models.enums import AuditAction')
text = text.replace('def listar_verificacoes(image_name: str, db: Session = Depends(get_db)):', 'def listar_verificacoes(image_name: str, db: Session = Depends(get_db)) -> list[dict[str, str]]:')
text = text.replace('def verificar_imagem(\n    aplicacao_id: int,', 'def verificar_imagem(\n    aplicacao_id: int,\n    image_ref: str,\n    db: Session = Depends(get_db),\n    usuario: User = Depends(RequirePermission("application:write"))\n) -> dict[str, str|int]:')
text = text.replace('r.criado_em', 'r.created_at')

with open('backend/app/routers/supply_chain.py', 'w', encoding='utf-8') as f:
    f.write(text)
