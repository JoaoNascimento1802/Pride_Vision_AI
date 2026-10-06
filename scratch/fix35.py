# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'from app\.database import SessionLocal',
    r'from app.database import _fabrica_de_sessoes',
    text
)

text = re.sub(
    r'            with SessionLocal\(\) as db:',
    r'            with _fabrica_de_sessoes()() as db:',
    text
)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed main.py")
