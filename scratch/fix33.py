import re

with open('backend/app/routers/vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'from app\.services\.sla_service import SlaService\nfrom app\.schemas\.vulnerability import SlaResponse, \(\nfrom app\.schemas\.vulnerability import \(',
    r'from app.schemas.vulnerability import (',
    text
)

with open('backend/app/routers/vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities.py imports")
