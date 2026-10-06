# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('ROADMAP_IMPLEMENTACAO.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'\| SLA \| 🟡 IMPLEMENTADO \| 🟢 \| 🟢 \| 🟢 \| 🟢 \| N/A \| Status histórico, réguas de prazo, aging, notificação e dashboard integrados\. \|',
    r'| SLA | 🟢 IMPLEMENTADO | 🟢 | 🟢 | 🟢 | 🟢 | N/A | Status histórico, réguas de prazo, aging, notificação e dashboard integrados. |',
    text
)

with open('ROADMAP_IMPLEMENTACAO.md', 'w', encoding='utf-8') as f:
    f.write(text)
print("updated ROADMAP")

