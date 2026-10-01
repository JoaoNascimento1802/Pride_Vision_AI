import pytest

from app.models.enums import Ferramenta
from app.services.normalizer import ler_gitleaks


def test_ler_gitleaks_valido():
    conteudo = """
    [
      {
        "Description": "AWS Manager ID",
        "StartLine": 1,
        "EndLine": 1,
        "StartColumn": 1,
        "EndColumn": 2,
        "Match": "AKIA1234567890ABCDEF",
        "Secret": "AKIA1234567890ABCDEF",
        "File": "config.yml",
        "Commit": "abc123def456",
        "RuleID": "aws-access-token",
        "Message": "",
        "Author": "author",
        "Email": "author@email.com",
        "Date": "2021-01-01T00:00:00Z",
        "Tags": ["key", "AWS"],
        "Repo": "owner/repo"
      }
    ]
    """
    resultado = ler_gitleaks(conteudo)
    assert resultado.ignorados == 0
    assert len(resultado.achados) == 1

    achado = resultado.achados[0]
    assert achado.origem == Ferramenta.GITLEAKS
    assert achado.endpoint == "config.yml:1"
    assert achado.severidade == "critical"
    assert achado.regra_id == "aws-access-token"
    assert achado.tipo_vuln == "secrets"
    assert achado.repository == "owner/repo"
    assert achado.commit == "abc123def456"
    assert achado.evidencia == "Segredo detectado (mascarado): AKIA**********\nCommit: abc123def456"
    # Ensure raw secret is not in evidence
    assert "AKIA1234567890ABCDEF" not in achado.evidencia


def test_ler_gitleaks_invalido():
    with pytest.raises(ValueError, match="não é um JSON válido"):
        ler_gitleaks("{invalido}")


def test_ler_gitleaks_nao_lista():
    with pytest.raises(ValueError, match="deve ser uma lista JSON"):
        ler_gitleaks('{"teste": 123}')
