# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('backend/app/models/__init__.py', 'r', encoding='utf-8') as f:
    text = f.read()

if "CloudAccount" not in text:
    text = text.replace('from app.models.container import', 'from app.models.cloud import CloudAccount, CloudResource\nfrom app.models.container import')
    text = text.replace('"ContainerInstance",', '"ContainerInstance",\n    "CloudAccount",\n    "CloudResource",')
    with open('backend/app/models/__init__.py', 'w', encoding='utf-8') as f:
        f.write(text)
