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
    (r"\bnao\b", "não"),
    (r"\bNao\b", "Não"),
]

def replace_in_string(match):
    text = match.group(0)
    # Only replace if the string has a space (sentences/messages)
    # OR if it's explicitly a title word and not used as a dict key
    # Wait, some labels might be single words like "Aplica\u00e7\u00e3o"
    if 'SELECT' in text or 'INSERT' in text or 'UPDATE' in text:
        return text
    if '/' in text and '-' in text: 
        return text
        
    original = text
    for pattern, replacement in fixes:
        text = re.sub(pattern, replacement, text)
    return text

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We match the string literal AND the following character (to check if it's a colon)
    # If the following character is a colon, we DON'T replace (it's a JSON key).
    def replacer(m):
        quote = m.group(1)
        inner = m.group(2)
        after = m.group(3)
        
        # Check if it's a dict key
        if after.strip().startswith(':'):
            return m.group(0) # Do nothing
            
        new_inner = replace_in_string(re.match(r'.*', inner)) # fake match
        
        # Do the real replacements on inner
        for pattern, replacement in fixes:
            inner = re.sub(pattern, replacement, inner)
            
        return f"{quote}{inner}{quote}{after}"

    new_content = re.sub(r'(["\'])(.*?)\1(\s*[:]?\s*)', replacer, content, flags=re.DOTALL)
        
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
