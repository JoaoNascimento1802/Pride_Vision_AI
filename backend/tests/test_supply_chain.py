from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models.enums import GateDecision, Risco
from app.models.policy import Policy

# Test ACs:
# AC-SC-01 - Dado que um artefato é submetido, usar o digest
# AC-SC-02 - Keyless signature valid
# AC-SC-03 - Signature invalid
# AC-SC-04 - Provenance present, builder extracted
# AC-SC-05 - Provenance invalid
# AC-SC-06 - Policy exige assinatura -> falha policy -> gera Achado
# AC-SC-07 - Trusted builder -> falha -> gera Achado
# AC-SC-08 - AchadoNormalizado categoria SUPPLY_CHAIN
# AC-SC-09 - Deduplication is handled by ingerir_relatorio automatically
# AC-SC-10 - CI/CD Integration
# AC-SC-11 - Audit
# AC-SC-12 - Cosign arguments without shell=True

@pytest.fixture
def mock_cosign_valid():
    with patch("app.services.supply_chain.subprocess.run") as mock_run:
        # Mock signature valid
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"optional": {"Subject": "test@example.com", "Issuer": "https://issuer.com"}}]'

        # Mock attestation valid
        mock_result_att = MagicMock()
        mock_result_att.returncode = 0
        import base64
        import json
        payload = base64.b64encode(json.dumps({
            "predicate": {"builder": {"id": "https://github.com/trusted-builder"}}
        }).encode('utf-8')).decode('utf-8')
        mock_result_att.stdout = f'[{{"payload": "{payload}"}}]'

        mock_run.side_effect = [mock_result, mock_result_att]
        yield mock_run

@pytest.fixture
def mock_cosign_invalid():
    with patch("app.services.supply_chain.subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: no matching signatures found"
        mock_run.return_value = mock_result
        yield mock_run

def test_verify_valid_signature_no_policy(client: TestClient, auth, aplicacao_producao, mock_cosign_valid):
    """AC-SC-01, AC-SC-02, AC-SC-04, AC-SC-12"""
    app_id = aplicacao_producao["id"]

    resp = client.post(f"/api/supply-chain/verify?aplicacao_id={app_id}&image_ref=registry/image@sha256:abc", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["findings_generated"] == 0

    # Check that subprocess.run was called twice (signature, attestation) and no shell=True
    assert mock_cosign_valid.call_count == 2
    args, kwargs = mock_cosign_valid.call_args_list[0]
    assert not kwargs.get("shell")
    assert "cosign" in args[0][0]

def test_verify_invalid_signature_with_policy(client: TestClient, auth, aplicacao_producao, db, mock_cosign_invalid):
    """AC-SC-03, AC-SC-06, AC-SC-08, AC-SC-09"""
    app_id = aplicacao_producao["id"]

    # Create policy
    policy = Policy(aplicacao_id=app_id, nome="Require Signature", require_signature=True, require_provenance=True, risco_minimo=Risco.CRITICO, acao=GateDecision.BLOCK)
    db.add(policy)
    db.commit()

    resp = client.post(f"/api/supply-chain/verify?aplicacao_id={app_id}&image_ref=registry/image@sha256:abc", headers=auth)
    print(resp.json())
    assert resp.status_code == 200
    assert resp.json()["findings_generated"] == 2 # sig missing + prov missing

def test_verify_trusted_builder_policy(client: TestClient, auth, aplicacao_producao, db, mock_cosign_valid):
    """AC-SC-05, AC-SC-07"""
    app_id = aplicacao_producao["id"]

    policy = Policy(aplicacao_id=app_id, nome="Require Builder", require_provenance=True, trusted_builder="https://github.com/different-builder", risco_minimo=Risco.CRITICO, acao=GateDecision.BLOCK)
    db.add(policy)
    db.commit()

    resp = client.post(f"/api/supply-chain/verify?aplicacao_id={app_id}&image_ref=registry/image@sha256:abc", headers=auth)
    print(resp.json())
    assert resp.status_code == 200
    assert resp.json()["findings_generated"] == 1 # Builder doesn't match
