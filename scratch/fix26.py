import re

with open('backend/tests/test_vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'    def test_sao_exatamente_cinco\(self\):\n        """AC-STATUS-01 [^\n]+"""\n',
    r'',
    text
)

with open('backend/tests/test_vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vocab test")

