import re

with open('backend/app/services/sla_policy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        Risco\.BAIXO: 90,\n        Risco\.INFORMATIVO: 0, # 0 means no SLA',
    r'        Risco.BAIXO: 90,',
    text
)

with open('backend/app/services/sla_policy.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed sla_policy.py")

