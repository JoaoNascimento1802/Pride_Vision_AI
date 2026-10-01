with open('ROADMAP_IMPLEMENTACAO.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('⚪ Multi-tenancy / SSO corporativo', '✅ Multi-tenancy / SSO corporativo')

with open('ROADMAP_IMPLEMENTACAO.md', 'w', encoding='utf-8') as f:
    f.write(text)
