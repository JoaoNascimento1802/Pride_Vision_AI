# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
ingestion.py — Orquestra a entrada de um relatório até a vulnerabilidade gravada.

Fluxo: ler o arquivo → gravar os achados → recorrelacionar tudo da aplicação →
classificar o risco → gravar as vulnerabilidades preservando o acompanhamento.

É a única camada que junta serviços puros com banco de dados. Os serviços de
normalização, correlação e risco continuam sem saber que existe persistência.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    Application,
    Ferramenta,
    Finding,
    StatusHistory,
    StatusVulnerabilidade,
    Upload,
    Vulnerability,
)
from app.services.correlator import correlacionar
from app.services.dominio import AchadoNormalizado, GrupoCorrelacionado, ResultadoParse
from app.services.normalizer import (
    endpoints_compativeis,
    ler_gitleaks,
    ler_nuclei,
    ler_semgrep,
    ler_trivy,
)
from app.services.risk_engine import (
    ContextoAplicacao,
    classificar,
    severidade_predominante,
)
from app.services.sla_service import SlaService


@dataclass
class ResultadoIngestao:
    """O que aconteceu com um upload, para a API devolver ao usuário."""

    upload_id: int
    ferramenta: Ferramenta
    achados_lidos: int
    achados_ignorados: int
    avisos: list[str]
    vulnerabilidades_totais: int
    vulnerabilidades_novas: int
    vulnerabilidades_atualizadas: int


def contexto_de(aplicacao: Application) -> ContextoAplicacao:
    """Extrai do modelo ORM os três fatores que o motor de risco usa."""
    return ContextoAplicacao(
        ambiente=aplicacao.ambiente,
        exposicao=aplicacao.exposicao,
        importancia=aplicacao.importancia,
    )


def _ler(ferramenta: Ferramenta, conteudo: str) -> ResultadoParse:
    if ferramenta is Ferramenta.SEMGREP:
        return ler_semgrep(conteudo)
    if ferramenta is Ferramenta.TRIVY:
        return ler_trivy(conteudo)
    if ferramenta is Ferramenta.GITLEAKS:
        return ler_gitleaks(conteudo)
    if ferramenta is Ferramenta.CHECKOV:
        from app.services.normalizer import ler_checkov
        return ler_checkov(conteudo)
    if ferramenta is Ferramenta.SUPPLY_CHAIN:
        from app.services.normalizer import ler_supply_chain
        return ler_supply_chain(conteudo)
    return ler_nuclei(conteudo)


def _gravar_achado(
    db: Session,
    aplicacao_id: int,
    upload_id: int,
    achado: AchadoNormalizado,
    container_id: int | None = None,
) -> Finding:
    registro = Finding(
        aplicacao_id=aplicacao_id,
        upload_id=upload_id,
        origem=achado.origem,
        tipo_vuln=achado.tipo_vuln,
        endpoint=achado.endpoint,
        severidade=achado.severidade,
        mensagem=achado.mensagem,
        regra_id=achado.regra_id,
        arquivo=achado.arquivo,
        linha=achado.linha,
        cwe=achado.cwe,
        url=achado.url,
        http_status=achado.http_status,
        evidencia=achado.evidencia,
        repository=achado.repository,
        commit=achado.commit,
        fingerprint=achado.fingerprint,
        resource=achado.resource,
        resource_type=achado.resource_type,
        iac_provider=achado.iac_provider,
        framework=achado.framework,
        guideline=achado.guideline,
        container_image_id=container_id,
        layer=achado.layer,
        pacote=achado.pacote,
        versao=achado.versao,
        versao_corrigida=achado.versao_corrigida,
    )
    db.add(registro)
    return registro


def _para_dominio(registro: Finding) -> AchadoNormalizado:
    """Converte um achado gravado de volta para o tipo puro do domínio."""
    return AchadoNormalizado(
        origem=registro.origem,
        tipo_vuln=registro.tipo_vuln,
        endpoint=registro.endpoint,
        severidade=registro.severidade,
        mensagem=registro.mensagem,
        regra_id=registro.regra_id,
        arquivo=registro.arquivo,
        linha=registro.linha,
        cwe=registro.cwe,
        url=registro.url,
        http_status=registro.http_status,
        evidencia=registro.evidencia,
        repository=registro.repository,
        commit=registro.commit,
        fingerprint=registro.fingerprint,
        layer=registro.layer,
        pacote=registro.pacote,
        versao=registro.versao,
        versao_corrigida=registro.versao_corrigida,
        image_name=registro.container_image.name if registro.container_image else None,
        image_repository=registro.container_image.name if registro.container_image else None,
        image_tag=registro.container_image.tag if registro.container_image else None,
        image_digest=registro.container_image.digest if registro.container_image else None,
        os=registro.container_image.os if registro.container_image else None,
        architecture=registro.container_image.architecture if registro.container_image else None,
        registry=registro.container_image.registry_name if registro.container_image else None,
        base_image=registro.container_image.base_image if registro.container_image else None,
    )


def _chave(grupo: GrupoCorrelacionado) -> tuple[str, str]:
    return (grupo.tipo_vuln, grupo.endpoint)


def _encontrar_existente(
    existentes: list[Vulnerability],
    ja_usadas: set[int],
    grupo: GrupoCorrelacionado,
) -> Vulnerability | None:
    """
    Localiza a vulnerabilidade já gravada que corresponde a este grupo.

    A busca não é por igualdade exata do endpoint. Quando só o Semgrep havia
    reportado, a vulnerabilidade ficou registrada como "src/views/busca.py"; ao
    chegar o relatório do Nuclei, o mesmo problema passa a se chamar "/busca".
    São o mesmo item, e tratá-los como distintos apagaria o acompanhamento que o
    usuário já tinha feito.

    O conjunto `ja_usadas` impede que dois grupos reivindiquem o mesmo registro.
    """
    for vulnerabilidade in existentes:
        if vulnerabilidade.id in ja_usadas or vulnerabilidade.tipo_vuln != grupo.tipo_vuln:
            continue
        if vulnerabilidade.endpoint == grupo.endpoint:
            return vulnerabilidade

    for vulnerabilidade in existentes:
        if vulnerabilidade.id in ja_usadas or vulnerabilidade.tipo_vuln != grupo.tipo_vuln:
            continue
        if endpoints_compativeis(vulnerabilidade.endpoint, grupo.endpoint):
            return vulnerabilidade

    return None


def recorrelacionar(db: Session, aplicacao: Application) -> tuple[int, int, int]:
    """
    Recalcula as vulnerabilidades de uma aplicação a partir dos achados gravados.

    Precisa considerar TODOS os achados, não só os do upload atual: subir o
    relatório do Nuclei depois do Semgrep só produz correlação se os achados
    antigos entrarem na conta.

    O status de acompanhamento é preservado quando a vulnerabilidade já existia.
    Vulnerabilidades que deixaram de aparecer nos relatórios são removidas, pois
    a plataforma reflete o resultado da varredura mais recente.

    Returns:
        (total, novas, atualizadas)
    """
    registros = list(db.scalars(select(Finding).where(Finding.aplicacao_id == aplicacao.id)).all())

    # O correlacionador devolve os mesmos objetos que recebeu, então a
    # identidade serve de ponte de volta para o registro gravado. Comparar por
    # endpoint não funcionaria: o grupo adota um endpoint canônico que pode
    # diferir do endpoint de cada achado ("/busca" para um achado em
    # "src/views/busca.py").
    registro_por_achado: dict[int, Finding] = {}
    achados_dominio: list[AchadoNormalizado] = []
    for registro in registros:
        achado = _para_dominio(registro)
        achados_dominio.append(achado)
        registro_por_achado[id(achado)] = registro

    grupos = correlacionar(achados_dominio)
    contexto = contexto_de(aplicacao)

    existentes = list(
        db.scalars(select(Vulnerability).where(Vulnerability.aplicacao_id == aplicacao.id)).all()
    )

    novas = 0
    atualizadas = 0
    reaproveitadas: set[int] = set()

    for grupo in grupos:
        resultado = classificar(grupo, contexto)

        vulnerabilidade = _encontrar_existente(existentes, reaproveitadas, grupo)
        if vulnerabilidade is not None:
            reaproveitadas.add(vulnerabilidade.id)
            # O endpoint pode ter mudado: o Semgrep sozinho registrou
            # "src/views/busca.py" e, com a chegada do Nuclei, o grupo passou a
            # se chamar "/busca". Adotar o novo mantém a tela legível.
            vulnerabilidade.endpoint = grupo.endpoint

        if vulnerabilidade is None:
            # Risco e justificativa entram já na construção: são obrigatórios no
            # banco, e o flush logo abaixo falharia se ficassem para depois.
            from datetime import datetime
            now = datetime.now(UTC)
            vulnerabilidade = Vulnerability(
                identificada_em=now,
                due_at=SlaService.calcular_due_date(resultado.risco, now),
                aplicacao_id=aplicacao.id,
                tipo_vuln=grupo.tipo_vuln,
                endpoint=grupo.endpoint,
                status=StatusVulnerabilidade.NOVA,
                risco=resultado.risco,
                justificativa=resultado.justificativa,
            )
            db.add(vulnerabilidade)
            db.flush()  # precisa do id para ligar os achados e o histórico
            db.add(
                StatusHistory(
                    vulnerabilidade_id=vulnerabilidade.id,
                    status_anterior=None,
                    status_novo=StatusVulnerabilidade.NOVA,
                    comentario="Vulnerabilidade identificada na ingestão do relatório.",
                )
            )
            novas += 1
        else:
            atualizadas += 1

        # O status nunca é tocado aqui: é trabalho do usuário, não da ingestão
        vulnerabilidade.correlacionada = grupo.correlacionada
        vulnerabilidade.encontrada_semgrep = grupo.encontrada_semgrep
        vulnerabilidade.confirmada_nuclei = grupo.confirmada_nuclei
        vulnerabilidade.risco = resultado.risco
        vulnerabilidade.due_at = SlaService.calcular_due_date(resultado.risco, vulnerabilidade.identificada_em)
        vulnerabilidade.justificativa = resultado.justificativa
        vulnerabilidade.severidade_original = severidade_predominante(grupo)

        for achado in grupo.achados:
            registro_por_achado[id(achado)].vulnerabilidade_id = vulnerabilidade.id

    # Remove o que sumiu dos relatórios: a plataforma reflete a varredura atual
    for vulnerabilidade in existentes:
        if vulnerabilidade.id not in reaproveitadas:
            db.delete(vulnerabilidade)

    db.flush()
    return len(grupos), novas, atualizadas


def _obter_ou_criar_imagem(db: Session, aplicacao_id: int, achado: AchadoNormalizado) -> int | None:
    if not achado.image_name and not achado.image_digest and not achado.image_repository:
        return None
    from app.models.container import ContainerImage

    query = select(ContainerImage).where(ContainerImage.aplicacao_id == aplicacao_id)
    if achado.image_digest:
        query = query.where(ContainerImage.digest == achado.image_digest)
    elif achado.image_repository and achado.image_tag:
        query = query.where(
            ContainerImage.name == achado.image_repository, ContainerImage.tag == achado.image_tag
        )
    else:
        query = query.where(
            ContainerImage.name == (achado.image_repository or achado.image_name or "desconhecido")
        )

    imagem = db.scalars(query).first()
    if not imagem:
        imagem = ContainerImage(
            aplicacao_id=aplicacao_id,
            name=achado.image_repository or achado.image_name or "desconhecido",
            tag=achado.image_tag,
            digest=achado.image_digest,
            registry_name=achado.registry,
            base_image=achado.base_image,
            os=achado.os,
            architecture=achado.architecture,
        )
        db.add(imagem)
        db.flush()
    return imagem.id


def ingerir_relatorio(
    db: Session,
    aplicacao: Application,
    ferramenta: Ferramenta,
    nome_arquivo: str,
    conteudo: str,
) -> ResultadoIngestao:
    """
    Processa um relatório enviado para uma aplicação.

    O relatório anterior da mesma ferramenta é substituído: uma nova varredura
    representa o estado atual, e acumular achados antigos mostraria problemas já
    inexistentes.

    Raises:
        ValueError: se o conteúdo não puder ser interpretado.
    """
    resultado_parse = _ler(ferramenta, conteudo)

    # Fora o relatório anterior da mesma ferramenta (os achados saem em cascata)
    db.execute(
        delete(Upload).where(Upload.aplicacao_id == aplicacao.id, Upload.ferramenta == ferramenta)
    )
    db.flush()

    upload = Upload(
        aplicacao_id=aplicacao.id,
        ferramenta=ferramenta,
        nome_arquivo=nome_arquivo,
        tamanho_bytes=len(conteudo.encode("utf-8")),
        total_achados=len(resultado_parse.achados),
        total_ignorados=resultado_parse.ignorados,
    )
    db.add(upload)
    db.flush()

    for achado in resultado_parse.achados:
        container_id = _obter_ou_criar_imagem(db, aplicacao.id, achado)
        _gravar_achado(db, aplicacao.id, upload.id, achado, container_id)
    db.flush()

    total, novas, atualizadas = recorrelacionar(db, aplicacao)
    db.commit()

    return ResultadoIngestao(
        upload_id=upload.id,
        ferramenta=ferramenta,
        achados_lidos=len(resultado_parse.achados),
        achados_ignorados=resultado_parse.ignorados,
        avisos=resultado_parse.avisos,
        vulnerabilidades_totais=total,
        vulnerabilidades_novas=novas,
        vulnerabilidades_atualizadas=atualizadas,
    )


def reclassificar_aplicacao(db: Session, aplicacao: Application) -> int:
    """
    Recalcula o risco das vulnerabilidades após mudança no contexto de negócio.

    Chamada quando a aplicação muda de ambiente, exposição ou importância. Sem
    isso, o inventário e a priorização contariam histórias diferentes: a
    aplicação apareceria como sendo de teste enquanto suas vulnerabilidades
    continuariam classificadas como se estivessem em produção.

    Returns:
        Quantas vulnerabilidades tiveram o risco alterado.
    """
    registros = list(db.scalars(select(Finding).where(Finding.aplicacao_id == aplicacao.id)).all())
    if not registros:
        return 0

    grupos = {_chave(g): g for g in correlacionar([_para_dominio(r) for r in registros])}
    contexto = contexto_de(aplicacao)
    alteradas = 0

    for vulnerabilidade in db.scalars(
        select(Vulnerability).where(Vulnerability.aplicacao_id == aplicacao.id)
    ).all():
        grupo = grupos.get((vulnerabilidade.tipo_vuln, vulnerabilidade.endpoint))
        if grupo is None:
            continue

        resultado = classificar(grupo, contexto)
        if vulnerabilidade.risco is not resultado.risco:
            alteradas += 1
        vulnerabilidade.risco = resultado.risco
        vulnerabilidade.due_at = SlaService.calcular_due_date(resultado.risco, vulnerabilidade.identificada_em)
        vulnerabilidade.justificativa = resultado.justificativa

    db.commit()
    return alteradas
