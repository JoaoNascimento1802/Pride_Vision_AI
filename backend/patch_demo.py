# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re
with open('backend/popular_demo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace auth/registrar block
text = re.sub(r'# O usu.*?try:.*?except.*?j.*? existia.*?\}', '', text, flags=re.DOTALL)
text = text.replace('EMAIL = "ana@exemplo.com"', 'EMAIL = "admin@pride.com"')
text = text.replace('SENHA = "senha-de-demonstracao"', 'SENHA = "admin"')

with open('backend/popular_demo.py', 'w', encoding='utf-8') as f:
    f.write(text)