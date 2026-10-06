# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from app.models.audit import AuditLog
from app.models.enums import AuditAction, Risco, StatusSla, StatusVulnerabilidade
from app.models.vulnerability import Vulnerability
from app.services.sla_service import SlaService


@pytest.fixture
def now():
    return datetime(2025, 1, 10, 12, 0, 0, tzinfo=UTC)

class TestSlaCalculations:
    def test_ac_sla_01_calcular_due_date_por_risco(self, now):
        """AC-SLA-01 — Prazo por risco."""
        assert SlaService.calcular_due_date(Risco.CRITICO, now) == now + timedelta(days=5)
        assert SlaService.calcular_due_date(Risco.ALTO, now) == now + timedelta(days=15)
        assert SlaService.calcular_due_date(Risco.MEDIO, now) == now + timedelta(days=30)
        assert SlaService.calcular_due_date(Risco.BAIXO, now) == now + timedelta(days=90)

    def test_ac_sla_02_status_on_track(self, db, now):
        """AC-SLA-02 — Status ON_TRACK."""
        from app.models import Application
        from app.models.enums import Ambiente, Exposicao, Importancia
        app = Application(nome="App Test", ambiente=Ambiente.PRODUCAO, responsavel="Time A", exposicao=Exposicao.INTERNET, importancia=Importancia.ALTA)
        db.add(app)
        db.commit()
        vuln = Vulnerability(identificada_em=now, due_at=now + timedelta(days=5), status=StatusVulnerabilidade.NOVA)
        # Check from perspective of day 1 (4 dias restantes)
        estado = SlaService.calcular_estado(vuln, now + timedelta(days=1))
        assert estado["status"] == StatusSla.ON_TRACK
        assert estado["dias_restantes"] == 4
        assert estado["dias_em_atraso"] == 0

    def test_ac_sla_03_status_due_soon(self, db, now):
        """AC-SLA-03 — Status DUE_SOON (<= 2 dias)."""
        from app.models import Application
        from app.models.enums import Ambiente, Exposicao, Importancia
        app = Application(nome="App Test", ambiente=Ambiente.PRODUCAO, responsavel="Time A", exposicao=Exposicao.INTERNET, importancia=Importancia.ALTA)
        db.add(app)
        db.commit()
        vuln = Vulnerability(identificada_em=now, due_at=now + timedelta(days=5), status=StatusVulnerabilidade.NOVA)
        estado = SlaService.calcular_estado(vuln, now + timedelta(days=3)) # 2 dias restantes
        assert estado["status"] == StatusSla.DUE_SOON
        assert estado["dias_restantes"] == 2

    def test_ac_sla_04_status_overdue(self, db, now):
        """AC-SLA-04 — Status OVERDUE."""
        from app.models import Application
        from app.models.enums import Ambiente, Exposicao, Importancia
        app = Application(nome="App Test", ambiente=Ambiente.PRODUCAO, responsavel="Time A", exposicao=Exposicao.INTERNET, importancia=Importancia.ALTA)
        db.add(app)
        db.commit()
        vuln = Vulnerability(identificada_em=now, due_at=now + timedelta(days=5), status=StatusVulnerabilidade.NOVA)
        estado = SlaService.calcular_estado(vuln, now + timedelta(days=7)) # 2 dias atrasado
        assert estado["status"] == StatusSla.OVERDUE
        assert estado["dias_restantes"] == 0
        assert estado["dias_em_atraso"] == 2
        assert estado["idade_em_dias"] == 7

    def test_ac_sla_05_status_completed_antes_do_prazo(self, db, now):
        """AC-SLA-05 — COMPLETED trava o diff no resolved_at."""
        from app.models import Application
        from app.models.enums import Ambiente, Exposicao, Importancia
        app = Application(nome="App Test", ambiente=Ambiente.PRODUCAO, responsavel="Time A", exposicao=Exposicao.INTERNET, importancia=Importancia.ALTA)
        db.add(app)
        db.commit()
        vuln = Vulnerability(
            identificada_em=now,
            due_at=now + timedelta(days=5),
            status=StatusVulnerabilidade.CORRIGIDA,
            resolved_at=now + timedelta(days=3)
        )
        # Checking on day 10, it should still show as COMPLETED with 2 days remaining, and not overdue.
        estado = SlaService.calcular_estado(vuln, now + timedelta(days=10))
        assert estado["status"] == StatusSla.COMPLETED
        assert estado["dias_restantes"] == 2
        assert estado["dias_em_atraso"] == 0
        assert estado["idade_em_dias"] == 10

    def test_ac_sla_06_status_exempt_pausa(self, db, now):
        """AC-SLA-06 — Estados de isenção e pausa."""
        from app.models import Application
        from app.models.enums import Ambiente, Exposicao, Importancia
        app = Application(nome="App Test", ambiente=Ambiente.PRODUCAO, responsavel="Time A", exposicao=Exposicao.INTERNET, importancia=Importancia.ALTA)
        db.add(app)
        db.commit()
        vuln = Vulnerability(identificada_em=now, due_at=now + timedelta(days=5), status=StatusVulnerabilidade.FALSO_POSITIVO, atualizada_em=now+timedelta(days=1))
        estado = SlaService.calcular_estado(vuln, now + timedelta(days=10))
        assert estado["status"] == StatusSla.EXEMPT

        vuln.status = StatusVulnerabilidade.EXCECAO_TEMPORARIA
        estado = SlaService.calcular_estado(vuln, now + timedelta(days=10))
        assert estado["status"] == StatusSla.PAUSED

class TestSlaScheduler:
    def test_ac_sla_07_geracao_eventos_e_idempotencia(self, db, now):
        """AC-SLA-07 — Scheduler identifica SLA vencido e gera evento sem duplicar."""
        from app.models import Application
        from app.models.enums import Ambiente, Exposicao, Importancia
        app = Application(nome="App Test", ambiente=Ambiente.PRODUCAO, responsavel="Time A", exposicao=Exposicao.INTERNET, importancia=Importancia.ALTA)
        db.add(app)
        db.commit()
        vuln = Vulnerability(
            aplicacao_id=1,
            tipo_vuln="XSS",
            endpoint="/test",
            status=StatusVulnerabilidade.NOVA,
            risco=Risco.CRITICO,
            justificativa="x",
            identificada_em=now - timedelta(days=10),
            due_at=now - timedelta(days=5) # Venceu há 5 dias
        )
        db.add(vuln)
        db.commit()

        with patch.object(SlaService, '_now', return_value=now):
            # Deve detectar e rodar _process_breach
            with patch.object(SlaService, '_notify_ticketing') as mock_notify:
                SlaService.check_and_update_slas(db)
                mock_notify.assert_called_once()

        # O evento foi persistido?
        evento = db.query(AuditLog).filter(AuditLog.entity_id == vuln.id, AuditLog.action == AuditAction.SLA_BREACHED).first()
        assert evento is not None

        # Rodar de novo não deve duplicar o evento
        with patch.object(SlaService, '_now', return_value=now):
            with patch.object(SlaService, '_notify_ticketing') as mock_notify2:
                SlaService.check_and_update_slas(db)
                mock_notify2.assert_not_called()
