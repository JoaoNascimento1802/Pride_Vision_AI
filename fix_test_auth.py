import re

with open('backend/tests/test_multi_tenancy.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('def test_ac_mt_02_data_isolation(client: TestClient, db: Session, usuario_cadastrado: dict):', 'def test_ac_mt_02_data_isolation(client: TestClient, db: Session, auth: dict):')
text = text.replace('token = usuario_cadastrado["access_token"]\n    \n    # Request without explicit tenant ID uses default (1)\n    res = client.get("/api/v1/applications", headers={"Authorization": f"Bearer {token}"})', '# Request without explicit tenant ID uses default (1)\n    res = client.get("/api/v1/applications", headers=auth)')
text = text.replace('res2 = client.get("/api/v1/applications", headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": "2"})', 'h2 = auth.copy()\n    h2["X-Tenant-ID"] = "2"\n    res2 = client.get("/api/v1/applications", headers=h2)')

with open('backend/tests/test_multi_tenancy.py', 'w', encoding='utf-8') as f:
    f.write(text)
