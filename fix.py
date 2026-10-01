with open('backend/app/database.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('from typing import Any\n', '')
text = 'from typing import Any\n' + text
with open('backend/app/database.py', 'w', encoding='utf-8') as f:
    f.write(text)
