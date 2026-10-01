with open('backend/app/models/__init__.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"Vulnerability",', '"Vulnerability",\n    "ContainerInstance",')

with open('backend/app/models/__init__.py', 'w', encoding='utf-8') as f:
    f.write(text)
