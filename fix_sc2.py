import sys

with open('backend/app/routers/supply_chain.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('def check_policy(policy, signature_valid: bool, provenance_valid: bool, identity: str = None, issuer: str = None):', 'def check_policy(policy: Policy, signature_valid: bool, provenance_valid: bool, identity: str | None = None, issuer: str | None = None) -> bool:')

with open('backend/app/routers/supply_chain.py', 'w', encoding='utf-8') as f:
    f.write(text)
