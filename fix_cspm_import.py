# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/app/routers/cspm.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from app.services.risk_engine import RiskEngine\n', '')

with open('backend/app/routers/cspm.py', 'w', encoding='utf-8') as f:
    f.write(text)
