import re
import uuid

with open('backend/tests/test_runtime.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'App Test RT [0-9a-f]+', lambda x: f'App Test RT {uuid.uuid4().hex[:8]}', text)
text = re.sub(r'c_123', lambda x: f'c_{uuid.uuid4().hex[:8]}', text)
text = re.sub(r'c_456', lambda x: f'c_{uuid.uuid4().hex[:8]}', text)

with open('backend/tests/test_runtime.py', 'w', encoding='utf-8') as f:
    f.write(text)
