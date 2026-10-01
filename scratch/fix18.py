import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aguardando_validacao"\},\n            headers=auth,\n        \)\n        assert resp_falha\.status_code == 422',
    r'        resp_falha = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aguardando_validacao"},\n            headers=auth,\n        )\n        assert resp_falha.status_code == 422',
    text
)

text = re.sub(
    r'        resp = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln\[\'id\'\]\}/status",',
    r'        resp = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 12")

