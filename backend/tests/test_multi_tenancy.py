from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.enums import Ambiente, Exposicao, Importancia
from app.models.tenant import Tenant, TenantUser
from app.models.user import User


def test_ac_mt_01_sso_provisioning(client: TestClient, db: Session):
    """AC-MT-01 — Dado que um usuário faz login via SSO..."""
    # Create tenant
    t = Tenant(id=2, name="SSO Org", domain="corporate.com")
    db.add(t)
    db.commit()

    # Callback simulates IdP return
    res = client.get("/api/auth/sso/callback?email=joao@corporate.com")
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token

    u = db.query(User).filter_by(email="joao@corporate.com").first()
    assert u is not None
    assert u.senha_hash == "SSO_MANAGED"

    tu = db.query(TenantUser).filter_by(user_id=u.id, tenant_id=2).first()
    assert tu is not None

def test_ac_mt_02_data_isolation(client: TestClient, db: Session, auth: dict):
    """AC-MT-02 — Dado que o banco de dados armazena aplicações..."""
    # Tenant 1 is Default. Tenant 2 is another.
    t2 = Tenant(id=2, name="Other Org", domain="other.com")
    db.add(t2)
    db.commit()

    # App in Tenant 1
    app1 = Application(nome="App T1", responsavel="TI", url="http://", tenant_id=1, exposicao=Exposicao.INTERNA, ambiente=Ambiente.TESTE, importancia=Importancia.BAIXA)
    # App in Tenant 2
    app2 = Application(nome="App T2", responsavel="TI", url="http://", tenant_id=2, exposicao=Exposicao.INTERNA, ambiente=Ambiente.TESTE, importancia=Importancia.BAIXA)

    db.add_all([app1, app2])
    db.commit()



    res = client.get("/api/aplicacoes", headers=auth)
    assert res.status_code == 200

    h2 = auth.copy()
    h2["X-Tenant-ID"] = "2"
    res2 = client.get("/api/aplicacoes", headers=h2)
    assert res2.status_code == 403

def test_ac_mt_04_default_organization(db: Session):
    """AC-MT-04 — Dado uma base de dados legada..."""
    # Test just ensures default tenant is created and apps have it
    t = db.query(Tenant).filter_by(id=1).first()
    assert t is not None
    assert t.name == "Default Organization"
