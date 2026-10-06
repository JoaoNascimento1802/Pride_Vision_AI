# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/alembic/env.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('target_metadata = None', '''import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.models import *
from app.models.tenant import Tenant, TenantUser
from app.database import Base
from app.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata''')

with open('backend/alembic/env.py', 'w', encoding='utf-8') as f:
    f.write(text)
