import re

with open('backend/tests/test_ai.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        assert depois\["status"\] == "em_correcao"\n        assert depois\["status"\] == "em_analise"\n        assert depois\["status"\] == status_antes',
    r'        assert depois["status"] == status_antes',
    text
)

with open('backend/tests/test_ai.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed test ai")
