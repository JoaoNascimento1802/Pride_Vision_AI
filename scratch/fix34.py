# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/app/routers/vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        if "finding:close" not in get_permissions\(usuario\.role\):\n        perms = get_permissions\(usuario\.role\)\n        if "finding:close" not in perms:',
    r'        perms = get_permissions(usuario.role)\n        if "finding:close" not in perms:',
    text
)

with open('backend/app/routers/vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities.py perms")

