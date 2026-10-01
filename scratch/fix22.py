import re

with open('backend/app/routers/vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'        new_value=\{"status": dados\.status\.value\},\n        metadata_info=\{"comentario": dados\.comentario\} if dados\.comentario else None\n        metadata_info=metadata if metadata else None\n    \)',
    r'        new_value={"status": dados.status.value},\n        metadata_info=metadata if metadata else None\n    )',
    text
)

with open('backend/app/routers/vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities.py metadata")

