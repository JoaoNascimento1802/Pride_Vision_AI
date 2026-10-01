import pytest

from app.models.enums import Ferramenta
from app.services.normalizer import ler_trivy


def test_ler_trivy_valido():
    conteudo = """
    {
      "SchemaVersion": 2,
      "Results": [
        {
          "Target": "package-lock.json",
          "Vulnerabilities": [
            {
              "VulnerabilityID": "CVE-2023-1234",
              "PkgName": "express",
              "Title": "express vulneravel",
              "Severity": "HIGH"
            }
          ]
        }
      ]
    }
    """
    resultado = ler_trivy(conteudo)
    assert resultado.ignorados == 0
    assert len(resultado.achados) == 1

    achado = resultado.achados[0]
    assert achado.origem == Ferramenta.TRIVY
    assert achado.endpoint == "package-lock.json (express)"
    assert achado.severidade == "HIGH"
    assert achado.mensagem == "express vulneravel"
    assert achado.regra_id == "CVE-2023-1234"
    assert achado.tipo_vuln == "sca"


def test_ler_trivy_invalido():
    with pytest.raises(ValueError, match="não é um JSON válido"):
        ler_trivy("{invalido}")


def test_ler_trivy_nao_objeto():
    with pytest.raises(ValueError, match="deve ser um objeto JSON"):
        ler_trivy("[]")


def test_ler_trivy_container():
    """AC-CONT-01, AC-CONT-02, AC-CONT-04"""
    conteudo = """
    {
      "SchemaVersion": 2,
      "ArtifactName": "alpine:3.15",
      "ArtifactType": "container_image",
      "Metadata": {
        "OS": {
          "Family": "alpine",
          "Name": "3.15.0"
        },
        "ImageConfig": {
          "architecture": "amd64"
        },
        "RepoTags": [
          "registry.example.com/org/app:latest"
        ],
        "RepoDigests": [
          "registry.example.com/org/app@sha256:4edbd2beb5f79b00"
        ]
      },
      "Results": [
        {
          "Target": "alpine:3.15 (alpine 3.15.0)",
          "Class": "os-pkgs",
          "Type": "alpine",
          "Vulnerabilities": [
            {
              "VulnerabilityID": "CVE-2022-28391",
              "PkgName": "busybox",
              "InstalledVersion": "1.34.1-r3",
              "FixedVersion": "1.34.1-r4",
              "Severity": "HIGH"
            }
          ]
        }
      ]
    }
    """
    resultado = ler_trivy(conteudo)
    assert resultado.ignorados == 0
    assert len(resultado.achados) == 1

    achado = resultado.achados[0]
    assert achado.origem == Ferramenta.TRIVY
    assert achado.tipo_vuln == "container_vulnerability"
    assert achado.endpoint == "sha256:4edbd2beb5f79b00 (busybox)"
    assert achado.severidade == "HIGH"
    assert achado.regra_id == "CVE-2022-28391"

    assert achado.image_name == "alpine:3.15"
    assert achado.image_repository == "registry.example.com/org/app"
    assert achado.image_tag == "latest"
    assert achado.image_digest == "sha256:4edbd2beb5f79b00"
    assert achado.os == "alpine 3.15.0"
    assert achado.architecture == "amd64"
    assert achado.pacote == "busybox"
    assert achado.versao == "1.34.1-r3"
    assert achado.versao_corrigida == "1.34.1-r4"
