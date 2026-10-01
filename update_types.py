with open('frontend/src/api/types.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '  criado_em: string\n}',
    '  criado_em: string\n  tenants?: { id: number; name: string }[]\n}'
)

with open('frontend/src/api/types.ts', 'w', encoding='utf-8') as f:
    f.write(text)
