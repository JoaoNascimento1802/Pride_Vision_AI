# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('frontend/src/api/types.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('permissions: string[]', 'permissions: string[]\n  tenants?: { id: number; name: string }[]')

with open('frontend/src/api/types.ts', 'w', encoding='utf-8') as f:
    f.write(text)
