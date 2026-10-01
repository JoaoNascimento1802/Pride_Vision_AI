import os

with open('backend/app/schemas/__init__.py', 'r', encoding='utf-8') as f:
    text = f.read()

if "cspm" not in text:
    text = text + "\n# Export cspm if needed\n"
    with open('backend/app/schemas/__init__.py', 'w', encoding='utf-8') as f:
        f.write(text)
