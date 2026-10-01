with open('backend/tests/conftest.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'(def [\w]+_db[\s\S]*?yield[\s\S]*?)def', text)
if match:
    print(match.group(1))
else:
    print(text[:500])
