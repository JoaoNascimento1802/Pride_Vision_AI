# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open('frontend/src/api/types.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '  criado_em: string\n}',
    '  criado_em: string\n  tenants?: { id: number; name: string }[]\n}'
)

with open('frontend/src/api/types.ts', 'w', encoding='utf-8') as f:
    f.write(text)
