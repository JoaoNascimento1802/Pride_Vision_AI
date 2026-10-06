# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_sla.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('app = Application(nome="App Teste SLA", owner="Team SLA")', 'app = Application(nome="App Teste SLA", responsavel="Team SLA", ambiente=Ambiente.DESENVOLVIMENTO, exposicao=Exposicao.INTERNA, importancia=Importancia.MEDIA)')

with open('backend/tests/test_sla.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("fixed")

