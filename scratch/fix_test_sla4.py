import re

with open('backend/tests/test_sla.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('ambiente=Ambiente.DESENVOLVIMENTO', 'ambiente=Ambiente.TESTE')

with open('backend/tests/test_sla.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("fixed sla test")

