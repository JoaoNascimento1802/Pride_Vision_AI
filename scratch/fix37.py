import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        resp = client\.patch\(\n            f"/api/vulnerabilidades/\{vuln_id\}/status",\n            json=\{"status": "aguardando_validacao"\},\n            headers=auth,\n        \)\n\n        assert resp\.status_code == 200\n        assert resp\.json\(\)\["resolved_at"\] is not None',
    r'        client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "aguardando_validacao"},\n            headers=auth,\n        )\n        resp = client.patch(\n            f"/api/vulnerabilidades/{vuln_id}/status",\n            json={"status": "corrigida"},\n            headers=auth,\n        )\n\n        assert resp.status_code == 200\n        assert resp.json()["resolved_at"] is not None',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed test 04")

