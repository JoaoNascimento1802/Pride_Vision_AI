import re

with open('backend/app/routers/vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'    audit\.log_action\(\n        action=AuditAction\.STATUS_CHANGED,\n        action=audit_action,',
    r'    audit.log_action(\n        action=audit_action,',
    text
)

with open('backend/app/routers/vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities.py action")

