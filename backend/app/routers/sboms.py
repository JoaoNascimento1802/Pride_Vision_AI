from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission, usuario_atual
from app.database import get_db
from app.models.application import Application
from app.models.sbom import Sbom, SbomComponent
from app.schemas.sbom import SbomComponentDetalhe, SbomDetalhe, SbomResumo
from app.services.sbom_parser import SbomParseResult, ler_sbom

router = APIRouter(prefix="/api", tags=["SBOM"], dependencies=[Depends(usuario_atual)])


@router.post(
    "/aplicacoes/{aplicacao_id}/sboms/import",
    response_model=SbomDetalhe,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_sbom(
    aplicacao_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("upload:create")),
) -> Any:
    aplicacao = db.get(Application, aplicacao_id)
    if not aplicacao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Aplicação não encontrada.")

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio.")

    # Detecção e parse
    try:
        resultado: SbomParseResult = ler_sbom(conteudo.decode("utf-8"))
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Persistência
    sbom = Sbom(
        aplicacao_id=aplicacao_id,
        formato=resultado.formato,
        versao_formato=resultado.versao_formato,
        nome_arquivo=arquivo.filename or "desconhecido",
        tamanho_bytes=len(conteudo),
        serial_number=resultado.serial_number,
        generated_at=resultado.generated_at,
    )
    db.add(sbom)
    db.flush()  # Para pegar o ID do SBOM

    # Adicionar componentes
    for comp in resultado.componentes:
        sbom_comp = SbomComponent(
            sbom_id=sbom.id,
            nome=comp.nome,
            versao=comp.versao,
            ecossistema=comp.ecossistema,
            tipo_componente=comp.tipo_componente,
            purl=comp.purl,
            cpe=comp.cpe,
            fornecedor=comp.fornecedor,
            licenca=comp.licenca,
            hashes=comp.hashes,
        )
        db.add(sbom_comp)

    db.commit()
    db.refresh(sbom)
    return sbom


@router.get("/aplicacoes/{aplicacao_id}/sboms", response_model=list[SbomResumo])
def listar_sboms(
    aplicacao_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> Any:
    stmt = select(Sbom).where(Sbom.aplicacao_id == aplicacao_id).order_by(Sbom.criado_em.desc())
    return list(db.scalars(stmt))


@router.get("/sboms/{sbom_id}", response_model=SbomDetalhe)
def obter_sbom(
    sbom_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> Any:
    sbom = db.get(Sbom, sbom_id)
    if not sbom:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="SBOM não encontrado.")
    return sbom


@router.get("/sboms/{sbom_id}/componentes", response_model=list[SbomComponentDetalhe])
def listar_componentes_sbom(
    sbom_id: int,
    db: Session = Depends(get_db),
    usuario: Any = Depends(RequirePermission("application:read")),
) -> Any:
    stmt = (
        select(SbomComponent).where(SbomComponent.sbom_id == sbom_id).order_by(SbomComponent.nome)
    )
    return list(db.scalars(stmt))
