# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import re

with open('frontend/src/testes/utilitarios.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('entrar: vi.fn(),\n            sair: vi.fn(),', 'entrar: vi.fn(),\n            sair: vi.fn(),\n            tenantId: "1",\n            setTenantId: vi.fn(),')
text = text.replace('entrar: async () => {},\n            sair: () => {},\n          }', 'entrar: async () => {},\n            sair: () => {},\n            tenantId: "1",\n            setTenantId: () => {},\n          }')

with open('frontend/src/testes/utilitarios.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
