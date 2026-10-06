# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('SDD/14-jira-ticketing-oauth.md', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("- **AC-JIRA-09** — Conexão Múltipla. A conexão é realizada via Integration associada ao usuário no sistema, permitindo operação baseada na conta Jira autorizada (3LO).\n", "")

with open('SDD/14-jira-ticketing-oauth.md', 'w', encoding='utf-8') as f:
    f.write(content)
print("sdd fixed")

