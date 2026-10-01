from app.models.enums import Ambiente, Exposicao, Ferramenta, Importancia, Risco
from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado
from app.services.risk_engine import ContextoAplicacao, classificar


def test_classificar_gitleaks_producao():
    grupo = GrupoCorrelacionado(
        tipo_vuln="secrets",
        endpoint="config.yml:1",
        achados=[
            AchadoNormalizado(
                origem=Ferramenta.GITLEAKS,
                tipo_vuln="secrets",
                endpoint="config.yml:1",
                severidade="critical",
                mensagem="teste",
                regra_id="aws-access-token",
                evidencia="mascarada",
            )
        ],
    )
    contexto = ContextoAplicacao(Ambiente.PRODUCAO, Exposicao.INTERNET, Importancia.ALTA)
    resultado = classificar(grupo, contexto)
    assert resultado.risco == Risco.CRITICO
    assert "verificação de segredos (Gitleaks)" in resultado.justificativa
