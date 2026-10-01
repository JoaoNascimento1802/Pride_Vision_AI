with open('backend/app/models/user.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    def __repr__(self)', '    tenant_users: Mapped[list["TenantUser"]] = relationship()\n\n    def __repr__(self)')

if 'TenantUser' not in text:
    text = text.replace('from typing import TYPE_CHECKING', 'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from app.models.tenant import TenantUser')

with open('backend/app/models/user.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('backend/app/schemas/auth.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

injection = """    @computed_field  # type: ignore[prop-decorator]
    @property
    def tenants(self) -> list[dict[str, str | int]]:
        if not hasattr(self, 'tenant_users') or not self.tenant_users:
            return [{"id": 1, "name": "Default Organization"}]
        return [{"id": tu.tenant.id, "name": tu.tenant.name} for tu in self.tenant_users]"""

text2 = text2.replace('class UsuarioResponse(BaseModel):', 'class UsuarioResponse(BaseModel):')
text2 = text2 + "\n" # wait I need to insert it inside the class
