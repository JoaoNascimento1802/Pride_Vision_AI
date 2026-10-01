import re

with open('backend/app/routers/vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        from app\.auth\.rbac import get_permissions\n\n        if "finding:close" not in get_permissions\(usuario\.role\):\n\n        if "finding:close" not in perms:\n            raise HTTPException\(',
    r'        from app.auth.rbac import get_permissions\n        perms = get_permissions(usuario.role)\n        if "finding:close" not in perms:\n            raise HTTPException(',
    text
)

with open('backend/app/routers/vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities.py")

