import re

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'async def _sla_scheduler\(\):\nasync def _sla_scheduler\(\) -> None:\n    """Executa a verificação de SLA periodicamente\."""',
    r'async def _sla_scheduler() -> None:\n    """Executa a verificação de SLA periodicamente."""',
    text
)

text = re.sub(
    r'            with SessionLocal\(\) as db:\n            with _fabrica_de_sessoes\(\)\(\) as db:',
    r'            with SessionLocal() as db:',
    text
)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed main.py")

