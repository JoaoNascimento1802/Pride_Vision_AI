import re

with open('backend/tests/test_remediation.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        assert resp\.json\(\)\["risk_acceptance_reason"\] == "Motivo"',
    r'        assert resp.json()["risk_acceptance_reason"] == "Motivo risco"',
    text
)

with open('backend/tests/test_remediation.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed test 17")
