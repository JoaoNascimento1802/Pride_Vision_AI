import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('res = client.get("/api/v1/applications", headers={"Authorization": f"Bearer {token}"})', 'res = client.get("/api/v1/applications", headers=auth)')

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
