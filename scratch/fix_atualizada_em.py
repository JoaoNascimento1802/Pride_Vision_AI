import os

with open('backend/app/services/sla_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'or vuln.atualizada_em',
    'or (vuln.atualizada_em.replace(tzinfo=timezone.utc) if vuln.atualizada_em and vuln.atualizada_em.tzinfo is None else vuln.atualizada_em)'
)

with open('backend/app/services/sla_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("atualizada_em fixed")

