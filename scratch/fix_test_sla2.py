import re

with open('backend/tests/test_sla.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('app = Application(nome="App Teste SLA", owner="Team SLA")', 'app = Application(nome="App Teste SLA", responsavel="Team SLA", ambiente=Ambiente.DESENVOLVIMENTO, exposicao=Exposicao.INTERNA, importancia=Importancia.MEDIA)')

with open('backend/tests/test_sla.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("fixed")

