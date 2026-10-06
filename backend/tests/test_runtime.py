# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.container import ContainerImage, ContainerInstance
from app.models.enums import Ambiente, Exposicao, Importancia, Risco, StatusVulnerabilidade
from app.models.ingestion import Finding
from app.models.vulnerability import Vulnerability
from app.routers.runtime import ingest_runtime_event
from app.schemas.runtime import FalcoEvent, FalcoOutputFields


def test_ac_rt_01_ingest_and_deduplicate(db: Session):
    """AC-RT-01 - Webhook."""
    app = Application(
        nome=f"App Test {uuid.uuid4().hex}",
        responsavel="Admin",
        ambiente=Ambiente.HOMOLOGACAO,
        importancia=Importancia.MEDIA,
        exposicao=Exposicao.INTERNA
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    img = ContainerImage(aplicacao_id=app.id, name="nginx", digest="sha256:123")
    db.add(img)
    db.commit()
    db.refresh(img)

    inst = ContainerInstance(container_id=f"c_{uuid.uuid4().hex}", container_image_id=img.id)
    db.add(inst)
    db.commit()

    event_payload = FalcoEvent(
        rule="Read sensitive file",
        priority="Warning",
        output="Warning Sensitive file opened for reading",
        time=datetime.now(UTC),
        output_fields=FalcoOutputFields(**{
            "container.id": inst.container_id,
            "proc.name": "cat",
            "evt.type": "open"
        })
    )

    for i in range(100):
        ingest_runtime_event(event=event_payload, authorization="Bearer pride-runtime-secret", db=db)

    findings = db.query(Finding).filter(Finding.container_id == inst.container_id).all()
    assert len(findings) == 1
    assert findings[0].hit_count == 100
    assert findings[0].regra_id == "Read sensitive file"

def test_ac_rt_02_reachability_correlation(db: Session):
    """AC-RT-02 - Reachability."""
    app = Application(
        nome=f"App Test {uuid.uuid4().hex}",
        responsavel="Admin",
        ambiente=Ambiente.HOMOLOGACAO,
        importancia=Importancia.MEDIA,
        exposicao=Exposicao.INTERNA
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    img = ContainerImage(aplicacao_id=app.id, name="log4j-app", digest="sha256:456")
    db.add(img)
    db.commit()
    db.refresh(img)

    inst = ContainerInstance(container_id=f"c_{uuid.uuid4().hex}", container_image_id=img.id)
    db.add(inst)
    db.commit()

    cve = Vulnerability(
        aplicacao_id=app.id,
        tipo_vuln="CVE-2021-44228 (log4j)",
        endpoint=f"container/{inst.container_id}",
        risco=Risco.ALTO,
        justificativa="Log4j detectado estaticamente",
        status=StatusVulnerabilidade.NOVA
    )
    db.add(cve)
    db.commit()
    db.refresh(cve)

    event_payload = FalcoEvent(
        rule="Unexpected process",
        priority="Critical",
        output="Unexpected process executed",
        time=datetime.now(UTC),
        output_fields=FalcoOutputFields(**{
            "container.id": inst.container_id,
            "proc.name": "log4j",
            "evt.type": "execve"
        })
    )

    resp = ingest_runtime_event(event=event_payload, authorization="Bearer pride-runtime-secret", db=db)

    assert resp.vulnerability_id == cve.id
    db.refresh(cve)
    assert cve.risco == Risco.CRITICO
