from app.models.enums import Ambiente, Exposicao, Ferramenta, Importancia, Risco
from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado
from app.services.risk_engine import ContextoAplicacao, classificar


def test_classificar_checkov():
    grupo = GrupoCorrelacionado(
        tipo_vuln="iac_misconfiguration",
        endpoint="aws_s3_bucket.main",
        achados=[
            AchadoNormalizado(
                origem=Ferramenta.CHECKOV,
                tipo_vuln="iac_misconfiguration",
                endpoint="aws_s3_bucket.main",
                severidade="HIGH",
                mensagem="teste",
                regra_id="CKV_AWS_18",
            )
        ],
    )
    contexto = ContextoAplicacao(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.BAIXA)
    resultado = classificar(grupo, contexto)
    assert resultado.risco == Risco.ALTO
    assert "verificação de infraestrutura (Checkov)" in resultado.justificativa
