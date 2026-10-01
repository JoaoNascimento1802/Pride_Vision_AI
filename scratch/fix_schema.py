import os

with open('backend/app/schemas/vulnerability.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'sla: SlaResponse | None = None' not in content:
    content = content.replace(
        'tem_analise_ia: bool = False',
        'tem_analise_ia: bool = False\n    sla: SlaResponse | None = None'
    )

with open('backend/app/schemas/vulnerability.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("schema fixed")

