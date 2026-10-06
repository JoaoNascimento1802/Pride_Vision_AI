# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/tests/conftest.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

replacement = """
    fabrica = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    sessao = fabrica()
    
    from app.models.tenant import Tenant
    if not sessao.query(Tenant).filter_by(id=1).first():
        sessao.add(Tenant(id=1, name="Default Organization", domain="default.local"))
        sessao.commit()
"""

text = re.sub(r'    fabrica = sessionmaker\(bind=engine, autocommit=False, autoflush=False\)\n    sessao = fabrica\(\)', replacement, text)

with open('backend/tests/conftest.py', 'w', encoding='utf-8') as f:
    f.write(text)
