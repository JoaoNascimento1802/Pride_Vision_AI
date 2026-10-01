from datetime import UTC, datetime
from app.models.remediation import RemediationComment, RemediationEvidence
from app.schemas.remediation import CommentCreate, CommentResponse, EvidenceCreate, EvidenceResponse
from app.schemas.vulnerability import AtribuicaoRequest
from app.services.state_machine import validar_transicao

@router.patch("/{vulnerabilidade_id}/owner", response_model=VulnerabilidadeDetalhe)
def atribuir_owner(
    vulnerabilidade_id: int,
    dados: AtribuicaoRequest,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:write")),
    audit: AuditService = Depends(get_audit_service),
) -> VulnerabilidadeDetalhe:
    """
    Atribui um responsável pela remediação da vulnerabilidade.
    """
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    anterior_id = vulnerabilidade.owner_id

    vulnerabilidade.owner_id = dados.owner_id
    vulnerabilidade.owner_team = dados.owner_team
    if dados.owner_id and not vulnerabilidade.assigned_at:
        vulnerabilidade.assigned_at = datetime.now(UTC)

    db.commit()
    
    audit.log_action(
        action=AuditAction.ASSIGNMENT_CHANGED,
        actor_user_id=usuario.id,
        entity_type=EntityType.FINDING,
        entity_id=str(vulnerabilidade.id),
        old_value={"owner_id": anterior_id},
        new_value={"owner_id": dados.owner_id, "owner_team": dados.owner_team},
    )
    
    return detalhar(vulnerabilidade_id, db)


@router.post("/{vulnerabilidade_id}/comments", response_model=CommentResponse)
def adicionar_comentario(
    vulnerabilidade_id: int,
    dados: CommentCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
    audit: AuditService = Depends(get_audit_service),
) -> CommentResponse:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    
    comentario = RemediationComment(
        vulnerability_id=vulnerabilidade.id,
        author_id=usuario.id,
        content=dados.content
    )
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    
    audit.log_action(
        action=AuditAction.COMMENT_ADDED,
        actor_user_id=usuario.id,
        entity_type=EntityType.COMMENT,
        entity_id=str(comentario.id),
        metadata_info={"vulnerability_id": vulnerabilidade.id}
    )
    
    resposta = CommentResponse.model_validate(comentario)
    resposta.author_name = usuario.nome
    return resposta


@router.get("/{vulnerabilidade_id}/comments", response_model=list[CommentResponse])
def listar_comentarios(
    vulnerabilidade_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
) -> list[CommentResponse]:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    
    resultados = []
    for c in vulnerabilidade.comments:
        item = CommentResponse.model_validate(c)
        item.author_name = c.author.nome if c.author else None
        resultados.append(item)
        
    return resultados


@router.post("/{vulnerabilidade_id}/evidences", response_model=EvidenceResponse)
def adicionar_evidencia(
    vulnerabilidade_id: int,
    dados: EvidenceCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:write")),
    audit: AuditService = Depends(get_audit_service),
) -> EvidenceResponse:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    
    evidencia = RemediationEvidence(
        vulnerability_id=vulnerabilidade.id,
        author_id=usuario.id,
        evidence_type=dados.evidence_type,
        description=dados.description,
        reference=dados.reference
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)
    
    audit.log_action(
        action=AuditAction.EVIDENCE_ADDED,
        actor_user_id=usuario.id,
        entity_type=EntityType.EVIDENCE,
        entity_id=str(evidencia.id),
        metadata_info={"vulnerability_id": vulnerabilidade.id, "type": dados.evidence_type}
    )
    
    resposta = EvidenceResponse.model_validate(evidencia)
    resposta.author_name = usuario.nome
    return resposta


@router.get("/{vulnerabilidade_id}/evidences", response_model=list[EvidenceResponse])
def listar_evidencias(
    vulnerabilidade_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
) -> list[EvidenceResponse]:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    
    resultados = []
    for e in vulnerabilidade.evidences:
        item = EvidenceResponse.model_validate(e)
        item.author_name = e.author.nome if e.author else None
        resultados.append(item)
        
    return resultados

