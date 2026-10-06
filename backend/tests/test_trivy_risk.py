# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from app.models.enums import Ambiente, Exposicao, Ferramenta, Importancia, Risco
from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado
from app.services.risk_engine import ContextoAplicacao, classificar


def test_classificar_trivy():
    grupo = GrupoCorrelacionado(
        tipo_vuln="sca",
        endpoint="pacote",
        achados=[
            AchadoNormalizado(
                origem=Ferramenta.TRIVY,
                tipo_vuln="sca",
                endpoint="pacote",
                severidade="HIGH",
                mensagem="teste",
                regra_id="CVE-123",
            )
        ],
    )
    contexto = ContextoAplicacao(Ambiente.PRODUCAO, Exposicao.INTERNA, Importancia.BAIXA)
    resultado = classificar(grupo, contexto)
    assert resultado.risco == Risco.ALTO
    assert "análise de composição (Trivy)" in resultado.justificativa
