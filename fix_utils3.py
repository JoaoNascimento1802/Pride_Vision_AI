import re

with open('frontend/src/testes/utilitarios.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('entrar: async () => {}, sair: () => {}', 'entrar: async () => {}, sair: () => {}, tenantId: "1", setTenantId: () => {}')

with open('frontend/src/testes/utilitarios.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
