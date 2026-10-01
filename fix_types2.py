import re

with open('frontend/src/api/types.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('permissions: string[]', 'permissions: string[]\n  tenants?: { id: number; name: string }[]')

with open('frontend/src/api/types.ts', 'w', encoding='utf-8') as f:
    f.write(text)
