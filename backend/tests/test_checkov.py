# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import pytest

from app.services.normalizer import ler_checkov


def test_ler_checkov_sucesso():
    """AC-IAC-01 — Parser extrai recursos, arquivo, linha e framework."""
    json_valido = """
    {
      "check_type": "terraform",
      "results": {
        "failed_checks": [
          {
            "check_id": "CKV_AWS_18",
            "check_name": "Ensure the S3 bucket has access logging enabled",
            "check_result": {"result": "FAILED"},
            "file_path": "/terraform/storage.tf",
            "file_line_range": [42, 45],
            "resource": "aws_s3_bucket.customer_data",
            "severity": "HIGH",
            "guideline": "https://docs.checkov.io/guidelines/..."
          }
        ]
      }
    }
    """
    res = ler_checkov(json_valido)
    assert len(res.achados) == 1
    assert res.ignorados == 0

    achado = res.achados[0]
    assert achado.tipo_vuln == "iac_misconfiguration"
    assert achado.regra_id == "CKV_AWS_18"
    assert achado.arquivo == "terraform/storage.tf"
    assert achado.linha == 42
    assert achado.resource == "aws_s3_bucket.customer_data"
    assert achado.resource_type == "aws_s3_bucket"
    assert achado.framework == "terraform"
    assert achado.severidade == "high"


def test_ler_checkov_arquivo_vazio():
    """AC-IAC-02 — Arquivo vazio levanta exceção."""
    with pytest.raises(ValueError, match="não é um JSON válido"):
        ler_checkov("")


def test_ler_checkov_json_invalido():
    """AC-IAC-03 — JSON inválido levanta exceção."""
    with pytest.raises(ValueError, match="não é um JSON válido"):
        ler_checkov("{broken")


def test_ler_checkov_campo_ausente():
    """AC-IAC-04 — Checkov report faltando campos cruciais é ignorado com aviso."""
    json_invalido = """
    {
      "results": {
        "failed_checks": [
          {
            "check_name": "Missing ID"
          }
        ]
      }
    }
    """
    res = ler_checkov(json_invalido)
    assert len(res.achados) == 0
    assert res.ignorados == 1
    assert len(res.avisos) > 0


def test_ler_checkov_multiplos():
    """AC-IAC-05 — Múltiplos findings no mesmo JSON (formato array)."""
    json_array = """
    [
      {
        "check_type": "terraform",
        "results": {
          "failed_checks": [
            {"check_id": "C1", "check_name": "N1"},
            {"check_id": "C2", "check_name": "N2"}
          ]
        }
      },
      {
        "check_type": "kubernetes",
        "results": {
          "failed_checks": [
            {"check_id": "C3", "check_name": "N3"}
          ]
        }
      }
    ]
    """
    res = ler_checkov(json_array)
    assert len(res.achados) == 3
    assert res.ignorados == 0
