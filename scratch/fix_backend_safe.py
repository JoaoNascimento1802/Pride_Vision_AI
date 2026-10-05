import os
import re

fixes = [
    (r"\baplicacao\b", "aplicação"),
    (r"\bAplicacao\b", "Aplicação"),
    (r"\baplicacoes\b", "aplicações"),
    (r"\bAplicacoes\b", "Aplicações"),
    (r"\busuario\b", "usuário"),
    (r"\bUsuario\b", "Usuário"),
    (r"\busuarios\b", "usuários"),
    (r"\bUsuarios\b", "Usuários"),
    (r"\bintegracao\b", "integração"),
    (r"\bIntegracao\b", "Integração"),
    (r"\bintegracoes\b", "integrações"),
    (r"\bIntegracoes\b", "Integrações"),
    (r"\bconfiguracao\b", "configuração"),
    (r"\bConfiguracao\b", "Configuração"),
    (r"\bconfiguracoes\b", "configurações"),
    (r"\bConfiguracoes\b", "Configurações"),
    (r"\bexposicao\b", "exposição"),
    (r"\bExposicao\b", "Exposição"),
    (r"\bcorrecao\b", "correção"),
    (r"\bCorrecao\b", "Correção"),
    (r"\bdecisao\b", "decisão"),
    (r"\bDecisao\b", "Decisão"),
    (r"\bavaliacao\b", "avaliação"),
    (r"\bAvaliacao\b", "Avaliação"),
    (r"\bacao\b", "ação"),
    (r"\bAcao\b", "Ação"),
    (r"\b'e\b", "é"),
    (r"\b~a\b", "ã"),
    (r"\b~o\b", "õ"),
    (r"Nao\b", "Não"),
    (r"\bnao\b", "não"),
]

def replace_in_string(match):
    text = match.group(0)
    # Exclude endpoints/urls or sql statements
    if 'SELECT' in text or 'INSERT' in text or 'UPDATE' in text:
        return text
    if '/' in text and '-' in text: # Looks like a url
        return text
    
    for pattern, replacement in fixes:
        text = re.sub(pattern, replacement, text)
    return text

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace ONLY inside double or single quotes
    # Match strings but ignore empty strings.
    new_content = re.sub(r'(["\'])(.*?)\1', replace_in_string, content, flags=re.DOTALL)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk('backend'):
    if 'node_modules' in root or '.venv' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))
