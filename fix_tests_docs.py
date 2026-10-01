with open('backend/tests/test_observability.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('def test_ac_obs_01_request_id_in_headers(client: TestClient, auth: dict[str, str]):', 'def test_ac_obs_01_request_id_in_headers(client: TestClient, auth: dict[str, str]):\n    """AC-OBS-01 — correlation_id"""')
text = text.replace('def test_ac_obs_03_metrics_protected_admin_only(', 'def test_ac_obs_03_metrics_protected_admin_only(\n    client: TestClient, db: Session, auth: dict[str, str], usuario_cadastrado: dict[str, str]\n):\n    """AC-OBS-03 — metrics admin"""\n')
text = text.replace('def test_ac_obs_04_deep_health_check(client: TestClient):', 'def test_ac_obs_04_deep_health_check(client: TestClient):\n    """AC-OBS-04 — deep health"""')
text = text.replace('def test_ac_obs_02_middleware_increments_metric(', 'def test_ac_obs_02_middleware_increments_metric(\n    client: TestClient, db: Session, auth: dict[str, str], usuario_cadastrado: dict[str, str]\n):\n    """AC-OBS-02 — middleware increments"""\n')

with open('backend/tests/test_observability.py', 'w', encoding='utf-8') as f:
    f.write(text)
