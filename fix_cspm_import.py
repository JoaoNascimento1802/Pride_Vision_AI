import re

with open('backend/app/routers/cspm.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from app.services.risk_engine import RiskEngine\n', '')

with open('backend/app/routers/cspm.py', 'w', encoding='utf-8') as f:
    f.write(text)
