# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_vulnerabilities.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('''            headers=auth,
            json={"status": "corrigida", "comentario": "Escaping aplicado"},
            json={"status": "em_correcao", "comentario": "Escaping aplicado"},
        )''', '''            headers=auth,
            json={"status": "em_correcao", "comentario": "Escaping aplicado"},
        )''')

content = content.replace('''            headers=auth,
            json={"status": "falso_positivo", "comentario": "Endpoint não existe mais"},
            json={"status": "falso_positivo", "comentario": "Endpoint não existe mais", "reason": "Mudança via teste"},
        )''', '''            headers=auth,
            json={"status": "falso_positivo", "comentario": "Endpoint não existe mais", "reason": "Mudança via teste"},
        )''')

with open('backend/tests/test_vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")

