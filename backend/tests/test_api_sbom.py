from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.enums import Ambiente, Exposicao, Importancia


def test_api_upload_sbom_cyclonedx(client: TestClient, db: Session, auth: dict[str, str]):
    app = Application(
        nome="App SBOM",
        responsavel="Time",
        ambiente=Ambiente.PRODUCAO,
        exposicao=Exposicao.INTERNA,
        importancia=Importancia.BAIXA,
    )
    db.add(app)
    db.commit()

    conteudo = b"""{
      "bomFormat": "CycloneDX",
      "specVersion": "1.4",
      "components": [
        { "name": "lodash", "version": "4.17.20" }
      ]
    }"""

    resp = client.post(
        f"/api/aplicacoes/{app.id}/sboms/import",
        headers=auth,
        files={"arquivo": ("sbom.json", conteudo, "application/json")},
    )
    assert resp.status_code == 201
    dados = resp.json()
    assert dados["formato"] == "cyclonedx"
    assert dados["versao_formato"] == "1.4"
    assert len(dados["componentes"]) == 1
    assert dados["componentes"][0]["nome"] == "lodash"
    assert dados["componentes"][0]["versao"] == "4.17.20"

    # Listar SBOMs da app
    resp2 = client.get(f"/api/aplicacoes/{app.id}/sboms", headers=auth)
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1

    # Detalhar componentes
    sbom_id = resp2.json()[0]["id"]
    resp3 = client.get(f"/api/sboms/{sbom_id}/componentes", headers=auth)
    assert resp3.status_code == 200
    assert len(resp3.json()) == 1
    assert resp3.json()[0]["nome"] == "lodash"
