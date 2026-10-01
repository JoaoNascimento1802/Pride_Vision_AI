with open('backend/app/routers/auth.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('from app.models.tenant import Tenant, TenantUser'):
        continue
    new_lines.append(line)

imports = "from app.models.tenant import Tenant, TenantUser\nfrom app.models.enums import Role\n"

# find from app.models import User
for i, line in enumerate(new_lines):
    if line.startswith('from app.models import User'):
        new_lines.insert(i+1, imports)
        break

with open('backend/app/routers/auth.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
