import uuid
import re

with open('backend/tests/test_runtime.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'nome="App Test[^"]+"', 'nome=f"App Test {uuid.uuid4().hex}"', text)
text = re.sub(r'container_id="c_[^"]+"', 'container_id=f"c_{uuid.uuid4().hex}"', text)
text = re.sub(r'"c_[0-9a-f]+"', 'inst.container_id', text)

with open('backend/tests/test_runtime.py', 'w', encoding='utf-8') as f:
    f.write(text)
