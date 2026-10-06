# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        resp = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/owner",\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "corrigida"\},\n            headers=auth,\n        \)',
    r'        client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/owner",\n            json={"owner_id": 1, "owner_team": "AppSec"},\n            headers=auth\n        )\n        resp = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "corrigida"},\n            headers=auth\n        )',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed test 01")

