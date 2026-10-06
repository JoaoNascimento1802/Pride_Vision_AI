# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import os
import re

fixes = [
    (r"\bAplica\u00e7\u00e3o\b", "Aplicação"),
    (r"\baplicacao\b(?!\s*=|\s*:)", "aplicação"),
    (r"\bAplicacao\b", "Aplicação"),
    (r"\bAplica\u00e7\u00f5es\b", "Aplicações"),
    (r"\bAplicacoes\b", "Aplicações"),
    (r"\bUsuario\b", "Usuário"),
    (r"\busuarios\b(?!\s*=|\s*:)", "usuários"),
    (r"\bUsuarios\b", "Usuários"),
    (r"\bIntegracao\b", "Integração"),
    (r"\bIntegracoes\b", "Integrações"),
    (r"\bConfiguracao\b", "Configuração"),
    (r"\bConfiguracoes\b", "Configurações"),
    (r"\bExposicao\b", "Exposição"),
    (r"\bCorrecao\b", "Correção"),
    (r"\bDecisao\b", "Decisão"),
    (r"\bAvaliacao\b", "Avaliação"),
    (r"\bAcao\b", "Ação"),
    (r"\b'e\b", "é"),
    (r"\b~a\b", "ã"),
    (r"\b~o\b", "õ"),
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, replacement in fixes:
        new_content = re.sub(pattern, replacement, new_content)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk('backend'):
    if 'node_modules' in root or '.venv' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))
