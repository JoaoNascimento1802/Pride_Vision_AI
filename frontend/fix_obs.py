# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

with open('src/pages/Observability.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(r'className=\{([^\"\'\`\}]+)\}', r'className="\1"', text)

with open('src/pages/Observability.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
