# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''    def test_ac_rem_23_sla_campos(self, client: TestClient, auth, cenario):
        """AC-REM-23 — SLA campos de tempo na Corrigida."""
        resp_lista = client.get("/api/vulnerabilidades", headers=auth)
        vuln_id = resp_lista.json()[0]["id"]
        client.patch(f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise"}, headers=auth)
        client.patch(f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_correcao"}, headers=auth)
        
        resp_falha = client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "corrigida"},
            headers=auth,
        )
        assert resp_falha.status_code == 422

        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "aguardando_validacao"},
            headers=auth,
        )
        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status",
            json={"status": "corrigida"},
            headers=auth,
        )

        resp = client.get(f"/api/vulnerabilidades/{vuln_id}", headers=auth)
        assert "detected_at" in resp.json() or "identificada_em" in resp.json()
        assert resp.json()["resolved_at"] is not None'''

text = re.sub(
    r'    def test_ac_rem_23_sla_campos.*?assert resp\.json\(\)\["resolved_at"\] is not None',
    replacement,
    text,
    flags=re.DOTALL
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed test 23")

