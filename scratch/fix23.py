import re

with open('backend/app/services/ingestion.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'    if ferramenta is Ferramenta\.CHECKOV:\n        from app\.services\.sla_service import SlaService\nfrom app\.services\.normalizer import ler_checkov\n        from app\.services\.normalizer import ler_checkov\n\n        return ler_checkov\(conteudo\)',
    r'    if ferramenta is Ferramenta.CHECKOV:\n        from app.services.normalizer import ler_checkov\n\n        return ler_checkov(conteudo)',
    text
)

with open('backend/app/services/ingestion.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed ingestion.py")

