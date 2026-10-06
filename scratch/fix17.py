# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1
text = re.sub(
    r'        resp = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "falso_positivo", "reason": "Motivo"\},\n            headers=auth,\n        \)',
    r'        resp_sucesso = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "falso_positivo", "reason": "Motivo"},\n            headers=auth,\n        )',
    text
)

# Fix 2
text = re.sub(
    r'        resp = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aceito_como_risco", "reason": "Baixo impacto no neg[oó]cio"\},\n            json=\{"status": "aceito_como_risco"\},\n            headers=auth,\n        \)',
    r'        resp_sucesso = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"},\n            headers=auth,\n        )',
    text
)

# Fix 3
text = re.sub(
    r'        vuln_id = vuln\["id"\]\n\n        resp = client\.patch\(',
    r'        vuln_id = vuln["id"]\n\n        resp = client.patch(',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 11")

