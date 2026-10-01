import re

with open('backend/app/models/__init__.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from app.models.user import User', 'from app.models.user import User\nfrom app.models.tenant import Tenant, TenantUser')
text = text.replace('"User",', '"User",\n    "Tenant",\n    "TenantUser",')

with open('backend/app/models/__init__.py', 'w', encoding='utf-8') as f:
    f.write(text)
