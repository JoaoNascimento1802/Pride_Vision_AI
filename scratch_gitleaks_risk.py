from pathlib import Path

content = Path('backend/app/services/risk_engine.py').read_text(encoding='utf-8')

old_str = """    else:
        origem = "análise de composição (Trivy)"
        faltando = "sem confirmação de outras ferramentas\""""

new_str = """    elif grupo.achado_de(Ferramenta.TRIVY):
        origem = "análise de composição (Trivy)"
        faltando = "sem confirmação de outras ferramentas"
    elif grupo.achado_de(Ferramenta.GITLEAKS):
        origem = "verificação de segredos (Gitleaks)"
        faltando = "sem confirmação de outras ferramentas"
    else:
        origem = "outra ferramenta"
        faltando = "sem confirmação\""""

if old_str in content:
    content = content.replace(old_str, new_str)
    Path('backend/app/services/risk_engine.py').write_text(content, encoding='utf-8')

