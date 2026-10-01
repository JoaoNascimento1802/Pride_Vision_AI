import re

with open('backend/tests/test_vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        assert ultimo\["status_anterior"\] == "em_analise"\n        assert ultimo\["status_novo"\] == "corrigida"\n        assert ultimo\["status_novo"\] == "em_correcao"\n        assert ultimo\["usuario_nome"\] == "Ana Souza"',
    r'        assert ultimo["status_anterior"] == "em_analise"\n        assert ultimo["status_novo"] == "em_correcao"\n        assert ultimo["usuario_nome"] == "Ana Souza"',
    text
)

with open('backend/tests/test_vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vocab test author")

