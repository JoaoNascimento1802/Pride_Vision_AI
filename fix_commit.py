import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('db.add(t2)', 'db.add(t2)\n    db.commit()')

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
