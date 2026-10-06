# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re
import glob

def add_tenant_id(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if "tenant_id" in text:
        return

    # find __tablename__ = ...
    # insert tenant_id after that
    pattern = r'(__tablename__\s*=\s*"[^"]+")'
    replacement = r'\1\n\n    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, default=1)'
    
    # We must add ForeignKey to imports if not present
    if 'ForeignKey' not in text:
        text = text.replace('from sqlalchemy import ', 'from sqlalchemy import ForeignKey, ')
    
    new_text = re.sub(pattern, replacement, text, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)

for model in ['application.py', 'cloud.py', 'policy.py', 'integration.py']:
    add_tenant_id(f'backend/app/models/{model}')
