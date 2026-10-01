import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('''        resp_post = client.post(

        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise"}, headers=auth
        )''', '''        client.patch(
            f"/api/vulnerabilidades/{vuln_id}/status", json={"status": "em_analise"}, headers=auth
        )''')

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 2")

