import re

# Fix database.py
with open('backend/app/database.py', 'r', encoding='utf-8') as f:
    db_text = f.read()
db_text = db_text.replace('from typing import Any\n', '')
db_text = db_text.replace('from collections.abc import Iterator', 'from collections.abc import Iterator\nfrom typing import Any')
with open('backend/app/database.py', 'w', encoding='utf-8') as f:
    f.write(db_text)

# Fix user.py
with open('backend/app/models/user.py', 'r', encoding='utf-8') as f:
    user_text = f.read()

if 'relationship' not in user_text:
    user_text = user_text.replace('from sqlalchemy.orm import Mapped, mapped_column', 'from sqlalchemy.orm import Mapped, mapped_column, relationship')

with open('backend/app/models/user.py', 'w', encoding='utf-8') as f:
    f.write(user_text)

