# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import json
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import RequirePermission
from app.database import get_db
from app.models.application import Application
from app.models.enums import AuditAction, Ferramenta
from app.models.policy import Policy
from app.models.supply_chain import ArtifactVerification
from app.models.user import User
from app.services.audit import AuditService, get_audit_service
from app.services.ingestion import ingerir_relatorio
from app.services.supply_chain import CosignService

router = APIRouter(prefix="/api/supply-chain", tags=["Supply Chain"])

@router.post("/verify")
def verify_artifact(
    aplicacao_id: int,
    image_ref: str,
    identity: str | None = None,
    issuer: str | None = None,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:write")),
    audit: AuditService = Depends(get_audit_service)
) -> dict[str, Any]:
    app_db = db.query(Application).filter(Application.id == aplicacao_id).first()
    if not app_db:
        return {"error": "Application not found"}

    audit.log_action(AuditAction.SUPPLY_CHAIN_VERIFICATION_STARTED, usuario.id, None, str(aplicacao_id), metadata_info={"image_ref": image_ref})
    svc = CosignService()

    # Verify Signature
    sig_result = svc.verify_signature(image_ref, identity, issuer)

    # Verify Attestation
    att_result = svc.verify_attestation(image_ref, identity, issuer)

    digest = image_ref.split("@")[-1] if "@" in image_ref else image_ref

    record = ArtifactVerification(
        aplicacao_id=aplicacao_id,
        artifact_reference=image_ref,
        artifact_digest=digest,
        signature_present=sig_result.signature_valid,
        signature_valid=sig_result.signature_valid,
        signer_identity=sig_result.signer_identity,
        certificate_issuer=sig_result.certificate_issuer,
        attestation_present=att_result.provenance_valid,
        provenance_present=att_result.provenance_valid,
        provenance_valid=att_result.provenance_valid,
        builder=att_result.builder,
        verification_log=sig_result.error_message or att_result.error_message
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Check policies
    policies = db.query(Policy).filter(
        Policy.ativa.is_(True),
        (Policy.aplicacao_id.is_(None)) | (Policy.aplicacao_id == aplicacao_id)
    ).all()

    req_sig = any(p.require_signature for p in policies)
    req_prov = any(p.require_provenance for p in policies)
    trusted_builders = [p.trusted_builder for p in policies if p.trusted_builder]

    findings = []

    if req_sig and not sig_result.signature_valid:
        findings.append({
            "titulo": "SIGNATURE_INVALID",
            "descricao": f"Artifact signature verification failed: {sig_result.error_message}",
            "severidade": "CRITICO",
            "arquivo": image_ref
        })

    if req_prov and not att_result.provenance_valid:
        findings.append({
            "titulo": "PROVENANCE_MISSING",
            "descricao": f"Artifact provenance verification failed: {att_result.error_message}",
            "severidade": "ALTO",
            "arquivo": image_ref
        })

    if trusted_builders and att_result.builder not in trusted_builders:
        findings.append({
            "titulo": "BUILDER_UNTRUSTED",
            "descricao": f"Builder {att_result.builder} is not trusted.",
            "severidade": "ALTO",
            "arquivo": image_ref
        })

    if findings:
        payload = json.dumps(findings)
        ingerir_relatorio(db, app_db, Ferramenta.SUPPLY_CHAIN, "supply_chain.json", payload)

    audit.log_action(AuditAction.SUPPLY_CHAIN_VERIFICATION_FINISHED, usuario.id, None, str(aplicacao_id), metadata_info={"verification_id": record.id})
    return {"status": "success", "verification_id": record.id, "findings_generated": len(findings)}

@router.get("/verifications")
def list_verifications(
    image_name: str,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("application:read"))
) -> list[dict[str, Any]]:
    # Procure qualquer verificação que o artefato coincida com a referência
    records = db.query(ArtifactVerification).filter(ArtifactVerification.artifact_reference.like(f"%{image_name}%")).order_by(ArtifactVerification.verified_at.desc()).all()
    return [{
        "id": r.id,
        "artifact_reference": r.artifact_reference,
        "signature_valid": r.signature_valid,
        "signer_identity": r.signer_identity,
        "provenance_valid": r.provenance_valid,
        "builder": r.builder,
        "criado_em": r.verified_at.isoformat()
    } for r in records]
