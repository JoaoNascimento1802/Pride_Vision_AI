# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/pyproject.toml', 'r', encoding='utf-8') as f:
    text = f.read()

deps = '"httpx>=0.27",\n    "cryptography>=43.0",\n    "prometheus-client>=0.20",\n    "python-json-logger>=2.0",\n    "alembic>=1.13",'
text = text.replace('"httpx>=0.27",\n    "cryptography>=43.0",\n    "prometheus-client>=0.20",\n    "python-json-logger>=2.0",', deps)

with open('backend/pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(text)
