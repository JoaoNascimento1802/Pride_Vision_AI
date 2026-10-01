import pytest

from app.services.sbom_parser import ler_sbom


def test_ler_cyclonedx():
    conteudo = """
    {
      "bomFormat": "CycloneDX",
      "specVersion": "1.4",
      "serialNumber": "urn:uuid:12345",
      "metadata": {
        "timestamp": "2023-10-01T12:00:00Z"
      },
      "components": [
        {
          "type": "library",
          "name": "lodash",
          "version": "4.17.20",
          "purl": "pkg:npm/lodash@4.17.20",
          "licenses": [
            { "license": { "id": "MIT" } }
          ]
        }
      ]
    }
    """
    resultado = ler_sbom(conteudo)
    assert resultado.formato == "cyclonedx"
    assert resultado.versao_formato == "1.4"
    assert resultado.serial_number == "urn:uuid:12345"
    assert len(resultado.componentes) == 1

    comp = resultado.componentes[0]
    assert comp.nome == "lodash"
    assert comp.versao == "4.17.20"
    assert comp.tipo_componente == "library"
    assert comp.purl == "pkg:npm/lodash@4.17.20"
    assert comp.ecossistema == "npm"
    assert comp.licenca == "MIT"


def test_ler_spdx():
    conteudo = """
    {
      "spdxVersion": "SPDX-2.3",
      "documentNamespace": "http://spdx.org/spdxdocs/spdx-example-444504E0-4F89-41D3-9A0C-0305E82C3301",
      "creationInfo": {
        "created": "2023-10-01T12:00:00Z"
      },
      "packages": [
        {
          "name": "glibc",
          "versionInfo": "2.11.1",
          "licenseConcluded": "GPL-2.0-only",
          "externalRefs": [
            {
              "referenceCategory": "PACKAGE-MANAGER",
              "referenceType": "purl",
              "referenceLocator": "pkg:deb/debian/glibc@2.11.1"
            }
          ]
        }
      ]
    }
    """
    resultado = ler_sbom(conteudo)
    assert resultado.formato == "spdx"
    assert resultado.versao_formato == "SPDX-2.3"
    assert len(resultado.componentes) == 1

    comp = resultado.componentes[0]
    assert comp.nome == "glibc"
    assert comp.versao == "2.11.1"
    assert comp.licenca == "GPL-2.0-only"
    assert comp.ecossistema == "deb"


def test_ler_invalido():
    with pytest.raises(ValueError, match="JSON válido"):
        ler_sbom("{invalido}")


def test_ler_formato_desconhecido():
    with pytest.raises(ValueError, match="Formato não suportado"):
        ler_sbom('{"teste": 123}')
