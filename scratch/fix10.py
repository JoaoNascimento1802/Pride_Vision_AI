import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('''        resp = client.post(
        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",''', '''        resp_post = client.post(
            f"/api/vulnerabilidades/{vuln_id}/evidences",''')

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed batch 4")

