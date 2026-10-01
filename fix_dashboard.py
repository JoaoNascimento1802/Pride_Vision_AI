import re

with open('backend/app/routers/dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

cloud_models = """
class CloudPosture(BaseModel):
    aws_issues: int
    gcp_issues: int
    azure_issues: int
    compliance_score: int
"""

if "CloudPosture" not in text:
    text = text.replace("class AplicacaoEmRisco(BaseModel):", cloud_models + "\nclass AplicacaoEmRisco(BaseModel):")
    text = text.replace("aplicacoes_em_risco: list[AplicacaoEmRisco]", "aplicacoes_em_risco: list[AplicacaoEmRisco]\n    cloud_posture: CloudPosture")
    
    # In visao_geral return
    text = text.replace("aplicacoes_em_risco=em_risco,", "aplicacoes_em_risco=em_risco,\n        cloud_posture=CloudPosture(aws_issues=2, gcp_issues=0, azure_issues=0, compliance_score=85),")

    with open('backend/app/routers/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(text)
