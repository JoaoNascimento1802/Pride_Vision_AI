# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/app/routers/vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'    anterior = vulnerabilidade\.status\n    vulnerabilidade\.status = dados\.status',
    r'    anterior = vulnerabilidade.status\n    vulnerabilidade.status = dados.status\n\n    if anterior == StatusVulnerabilidade.NOVA and dados.status != StatusVulnerabilidade.NOVA:\n        if not vulnerabilidade.owner_id:\n            vulnerabilidade.owner_id = usuario.id\n            vulnerabilidade.assigned_at = datetime.now(UTC)',
    text
)

with open('backend/app/routers/vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities owner_id")

