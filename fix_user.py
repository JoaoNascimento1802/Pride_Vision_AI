with open('backend/app/models/user.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('if TYPE_CHECKING:\n    from app.models.tenant import TenantUser', 'from app.models.tenant import TenantUser\nfrom sqlalchemy.orm import relationship')

with open('backend/app/models/user.py', 'w', encoding='utf-8') as f:
    f.write(text)
