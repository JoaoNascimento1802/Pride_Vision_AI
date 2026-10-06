# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('''    def test_ac_rem_13_lista_evidencias(self, client: TestClient, auth, cenario):
        """AC-REM-13 — Lista evidencias."""
        # Falha sem reason
        resp_falha = client.patch(

        client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",''', '''    def test_ac_rem_13_lista_evidencias(self, client: TestClient, auth, cenario):
        """AC-REM-13 — Lista evidencias."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        
        client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",''')

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 6")

