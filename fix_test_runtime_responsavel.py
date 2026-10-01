import re

with open('backend/tests/test_runtime.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'(app = Application\([^)]+)\)', r'\1, responsavel="Admin")', text)

with open('backend/tests/test_runtime.py', 'w', encoding='utf-8') as f:
    f.write(text)
