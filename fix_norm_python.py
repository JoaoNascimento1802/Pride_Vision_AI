with open('backend/app/services/normalizer.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
old_block = re.search(r"achado = AchadoNormalizado\([^)]+origem=Ferramenta\.API_SECURITY\n\s+\)", text)

if old_block:
    new_block = """achado = AchadoNormalizado(
                origem=Ferramenta.API_SECURITY,
                tipo_vuln=item.get("titulo", "API Security Finding"),
                endpoint=item.get("endpoint", ""),
                severidade=item.get("severidade", "medium"),
                mensagem=item.get("descricao", ""),
                regra_id=item.get("titulo", "API Security Finding"),
                evidencia=item.get("log", "")
            )"""
    text = text.replace(old_block.group(0), new_block)
    with open('backend/app/services/normalizer.py', 'w', encoding='utf-8') as f:
        f.write(text)

