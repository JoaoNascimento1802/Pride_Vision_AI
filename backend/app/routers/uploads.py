# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
uploads.py — Envio dos relatórios do Semgrep e do Nuclei.

A primeira versão recebe os arquivos manualmente; o sistema não executa as
ferramentas, conforme a especificação.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.config import settings
from app.database import get_db
from app.models import Application, Ferramenta, Upload
from app.schemas.upload import ResultadoUploadResponse, UploadResumo
from app.services import ingerir_relatorio

router = APIRouter(
    prefix="/api/aplicacoes/{aplicacao_id}",
    tags=["Uploads"],
    dependencies=[Depends(usuario_atual)],
)


def _buscar_aplicacao(db: Session, aplicacao_id: int) -> Application:
    aplicacao = db.get(Application, aplicacao_id)
    if aplicacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Aplicação não encontrada."
        )
    return aplicacao


async def _ler_conteudo(arquivo: UploadFile) -> str:
    """
    Lê o arquivo enviado como texto UTF-8, respeitando o limite de tamanho.

    O teto evita que um upload gigante consuma toda a memória do processo — o
    conteúdo é lido inteiro porque os parsers precisam do documento completo.
    """
    bruto = await arquivo.read()

    if len(bruto) > settings.MAX_UPLOAD_BYTES:
        limite_mb = settings.MAX_UPLOAD_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo maior que o limite de {limite_mb:.0f} MB.",
        )

    if not bruto.strip():
        raise HTTPException(
            status_code=422,
            detail="O arquivo enviado está vazio.",
        )

    try:
        return bruto.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail="O arquivo precisa estar codificado em UTF-8.",
        ) from exc


async def _processar(
    db: Session, aplicacao_id: int, ferramenta: Ferramenta, arquivo: UploadFile
) -> ResultadoUploadResponse:
    aplicacao = _buscar_aplicacao(db, aplicacao_id)
    conteudo = await _ler_conteudo(arquivo)

    try:
        resultado = ingerir_relatorio(
            db=db,
            aplicacao=aplicacao,
            ferramenta=ferramenta,
            nome_arquivo=arquivo.filename or f"{ferramenta.value}-sem-nome",
            conteudo=conteudo,
        )
    except ValueError as exc:
        # Arquivo com formato errado: a mensagem do parser já explica o problema
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ResultadoUploadResponse(
        upload_id=resultado.upload_id,
        ferramenta=resultado.ferramenta,
        ferramenta_label=resultado.ferramenta.label,
        achados_lidos=resultado.achados_lidos,
        achados_ignorados=resultado.achados_ignorados,
        avisos=resultado.avisos,
        vulnerabilidades_totais=resultado.vulnerabilidades_totais,
        vulnerabilidades_novas=resultado.vulnerabilidades_novas,
        vulnerabilidades_atualizadas=resultado.vulnerabilidades_atualizadas,
    )


@router.post(
    "/uploads/semgrep",
    response_model=ResultadoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_semgrep(
    aplicacao_id: int,
    arquivo: UploadFile = File(..., description="Relatório JSON gerado pelo Semgrep"),
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("upload:create")),
) -> ResultadoUploadResponse:
    """
    Recebe o relatório JSON do Semgrep.

    Substitui o relatório anterior desta ferramenta para a aplicação: uma nova
    varredura representa o estado atual. Em seguida recorrelaciona tudo e
    reclassifica o risco, preservando o status de acompanhamento já definido.
    """
    return await _processar(db, aplicacao_id, Ferramenta.SEMGREP, arquivo)


@router.post(
    "/uploads/nuclei",
    response_model=ResultadoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_nuclei(
    aplicacao_id: int,
    arquivo: UploadFile = File(..., description="Relatório JSONL gerado pelo Nuclei"),
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("upload:create")),
) -> ResultadoUploadResponse:
    """
    Recebe o relatório JSONL do Nuclei.

    É neste ponto que a correlação costuma acontecer: os achados do Nuclei
    encontram os do Semgrep já gravados e as duas confirmações se juntam.
    """
    return await _processar(db, aplicacao_id, Ferramenta.NUCLEI, arquivo)


@router.post(
    "/uploads/trivy",
    response_model=ResultadoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_trivy(
    aplicacao_id: int,
    arquivo: UploadFile = File(..., description="Relatório JSON gerado pelo Trivy"),
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("upload:create")),
) -> ResultadoUploadResponse:
    """
    Recebe o relatório JSON do Trivy (SCA).
    """
    return await _processar(db, aplicacao_id, Ferramenta.TRIVY, arquivo)


@router.post(
    "/uploads/gitleaks",
    response_model=ResultadoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_gitleaks(
    aplicacao_id: int,
    arquivo: UploadFile = File(..., description="Relatório JSON gerado pelo Gitleaks"),
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("upload:create")),
) -> ResultadoUploadResponse:
    """
    Recebe o relatório JSON do Gitleaks (Secrets).
    """
    return await _processar(db, aplicacao_id, Ferramenta.GITLEAKS, arquivo)


@router.post(
    "/uploads/checkov",
    response_model=ResultadoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_checkov(
    aplicacao_id: int,
    arquivo: UploadFile = File(..., description="Relatório JSON gerado pelo Checkov"),
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("upload:create")),
) -> ResultadoUploadResponse:
    """
    Recebe o relatório JSON do Checkov (IaC).
    """
    return await _processar(db, aplicacao_id, Ferramenta.CHECKOV, arquivo)


@router.get("/uploads", response_model=list[UploadResumo])
def listar_uploads(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> list[Upload]:
    """Relatórios atualmente em vigor para a aplicação, um por ferramenta."""
    _buscar_aplicacao(db, aplicacao_id)
    return list(
        db.scalars(
            select(Upload)
            .where(Upload.aplicacao_id == aplicacao_id)
            .order_by(Upload.criado_em.desc())
        ).all()
    )
