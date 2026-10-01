import re

with open('backend/app/models/user.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from app.models.enums import Role', 'from app.models.enums import Role\nfrom app.models.tenant import TenantUser')

with open('backend/app/models/user.py', 'w', encoding='utf-8') as f:
    f.write(text)
