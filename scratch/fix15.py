import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: Undefined resp_sucesso at 321
text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "falso_positivo", "reason": "É código de teste"\},\n            headers=auth\n        \)\n        assert resp_sucesso\.status_code == 200',
    r'        resp_sucesso = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "falso_positivo", "reason": "É código de teste"},\n            headers=auth\n        )\n        assert resp_sucesso.status_code == 200',
    text
)

# Fix 2: duplicate json at 340
text = re.sub(
    r'        resp_sucesso = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"\},\n            json=\{"status": "aceito_como_risco"\},\n            headers=auth,\n        \)',
    r'        resp_sucesso = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aceito_como_risco", "reason": "Baixo impacto no negócio"},\n            headers=auth,\n        )',
    text
)

# Fix 3: unused vuln_id at 357
text = re.sub(
    r'        vuln = next\(v for v in resp_lista\.json\(\) if v\["status"\] == "nova"\)\n        vuln_id = vuln\["id"\]\n\n        resp = client\.patch\(',
    r'        vuln = next(v for v in resp_lista.json() if v["status"] == "nova")\n        vuln_id = vuln["id"]\n\n        resp = client.patch(',
    text
)

# Fix 4: undefined resp_falha at 432
text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "corrigida"\},\n            headers=auth,\n        \)\n        assert resp_falha\.status_code == 422',
    r'        resp_falha = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "corrigida"},\n            headers=auth,\n        )\n        assert resp_falha.status_code == 422',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 9")

