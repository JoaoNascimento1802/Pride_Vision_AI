import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('ambiente=Ambiente.DESENVOLVIMENTO', 'ambiente=Ambiente.TESTE')

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
