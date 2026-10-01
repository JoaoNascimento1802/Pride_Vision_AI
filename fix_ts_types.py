import re

with open('frontend/src/api/types.ts', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """export interface Usuario {
  id: number
  email: string
  nome: string
  role: string
  criado_em: string
  permissions: string[]
  tenants?: { id: number; name: string }[]
}"""

text = re.sub(r'export interface Usuario \{[\s\S]*?criado_em: string\s*(role: string\s*)?\}', replacement, text)

with open('frontend/src/api/types.ts', 'w', encoding='utf-8') as f:
    f.write(text)
