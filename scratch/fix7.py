# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: 
text = text.replace('''            json={"owner_id": 1, "owner_team": "AppSec"},
            headers=auth
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "corrigida"}, headers=auth
        )''', '''            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "corrigida"}, headers=auth
        )''')

# Fix 2:
text = text.replace('''    def test_remediation_comments(self, client: TestClient, auth, cenario):
        """AC-REM-09 — Comentários em vulnerabilidades."""
    def test_ac_rem_03_fluxo_correcao(self, client: TestClient, auth, cenario):
        """AC-REM-03 — Fluxo EM_CORRECAO para AGUARDANDO_VALIDACAO."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        

        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments",
            json={"content": "Iniciando a correção conforme doc."},
            headers=auth
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise"}, headers=auth
        )''', '''    def test_remediation_comments(self, client: TestClient, auth, cenario):
        """AC-REM-09 — Comentários em vulnerabilidades."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]

        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/comments",
            json={"content": "Iniciando a correção conforme doc."},
            headers=auth
        )''')

# Fix 3:
text = text.replace('''            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "aguardando_validacao"}, headers=auth
        )''', '''            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth
        )''')

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 1")

