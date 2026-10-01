import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1
text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aguardando_validacao"\},\n            headers=auth,\n        \)\n\n        assert resp\.status_code == 200',
    r'        resp = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aguardando_validacao"},\n            headers=auth,\n        )\n\n        assert resp.status_code == 200',
    text
)

# Fix 2
text = re.sub(
    r'        assert evidences\[-1\]\["evidence_type"\] == "commit"\n        assert resp\.status_code == 200\n        assert resp\.json\(\)\["description"\] == "Desc"',
    r'        assert evidences[-1]["evidence_type"] == "commit"',
    text
)

# Fix 3
text = re.sub(
    r'        resp = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "falso_positivo"\},\n            headers=auth,\n        \)\n        assert resp_falha\.status_code == 422',
    r'        resp_falha = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "falso_positivo"},\n            headers=auth,\n        )\n        assert resp_falha.status_code == 422',
    text
)

# Fix 4
text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "falso_positivo", "reason": "Motivo"\},\n            headers=auth,\n        \)\n        assert resp_sucesso\.status_code == 200',
    r'        resp_sucesso = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "falso_positivo", "reason": "Motivo"},\n            headers=auth,\n        )\n        assert resp_sucesso.status_code == 200',
    text
)

# Fix 5
text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"\},\n            headers=auth,\n        \)\n        assert resp_sucesso\.status_code == 200',
    r'        resp_sucesso = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"},\n            headers=auth,\n        )\n        assert resp_sucesso.status_code == 200',
    text
)

# Fix 6
text = re.sub(
    r'        vuln_id = vuln\["id"\]\n\n        vuln_id = resp_lista\.json\(\)\[0\]\["id"\]',
    r'        vuln_id = vuln["id"]',
    text
)

# Fix 7
text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aceito_como_risco", "reason": "Motivo risco"\},\n            headers=auth,\n        \)\n        assert resp_falha\.status_code == 422',
    r'        resp_falha = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aceito_como_risco", "reason": "Motivo risco"},\n            headers=auth,\n        )\n        assert resp_falha.status_code == 422',
    text
)

# Fix 8
text = re.sub(
    r'        assert "detected_at" in resp\.json\(\) or "identificada_em" in resp\.json\(\)\n        assert resp\.json\(\)\["resolved_at"\] is not None',
    r'        resp = client.get(f"/api/vulnerabilidades/{vuln_id}", headers=auth)\n        assert "detected_at" in resp.json() or "identificada_em" in resp.json()\n        assert resp.json()["resolved_at"] is not None',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 8")

