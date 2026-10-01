import re
with open('backend/app/schemas/auth.py', 'r', encoding='utf-8') as f:
    text = f.read()

injection = """    @computed_field  # type: ignore[prop-decorator]
    @property
    def tenants(self) -> list[dict[str, str | int]]:
        if not hasattr(self, "tenant_users") or not self.tenant_users:
            return [{"id": 1, "name": "Default Organization"}]
        return [{"id": tu.tenant.id, "name": tu.tenant.name} for tu in getattr(self, "tenant_users", []) if getattr(tu, "tenant", None)]
"""

text = re.sub(r'(def permissions\(self\) -> list\[str\]:[\s\S]*?return get_permissions\(Role\(self\.role\)\))', r'\1\n\n' + injection, text)

with open('backend/app/schemas/auth.py', 'w', encoding='utf-8') as f:
    f.write(text)
