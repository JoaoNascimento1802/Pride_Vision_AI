import os
import re

folders = ["app/routers"]

def fix_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Add from typing import Any if not there
    if "from typing import Any" not in content and "Depends(RequirePermission" in content:
        content = content.replace("from fastapi import", "from typing import Any\nfrom fastapi import")

    # Replace `usuario = Depends(RequirePermission` with `usuario: Any = Depends(RequirePermission`
    content = re.sub(r'usuario\s*=\s*Depends\(RequirePermission', r'usuario: Any = Depends(RequirePermission', content)

    # We also need to add `-> Any:` to endpoints that miss return type.
    # It's easier to just append `-> Any` to def lines ending with `):` if they have `usuario` in it.

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.endswith('):') and 'def ' not in line: # It's usually the closing paren of params
            # Check if def is above
            is_def = False
            for j in range(i, max(-1, i-10), -1):
                if lines[j].strip().startswith('def '):
                    is_def = True
                    break
            if is_def and '->' not in line:
                lines[i] = line.replace('):', ') -> Any:')
        elif line.endswith('):') and 'def ' in line and '->' not in line:
            lines[i] = line.replace('):', ') -> Any:')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))


for root, _, files in os.walk("app/routers"):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))

