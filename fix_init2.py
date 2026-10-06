# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('backend/app/models/__init__.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"Vulnerability",', '"Vulnerability",\n    "ContainerInstance",')

with open('backend/app/models/__init__.py', 'w', encoding='utf-8') as f:
    f.write(text)
