import base64
import json
import logging
import subprocess

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CosignError(Exception):
    pass

class VerificationResult(BaseModel):
    artifact_reference: str
    signature_valid: bool
    signer_identity: str | None = None
    certificate_issuer: str | None = None
    provenance_valid: bool = False
    builder: str | None = None
    error_message: str | None = None

class CosignService:
    def __init__(self, bin_path: str = "backend/bin/cosign.exe"):
        self.bin_path = bin_path

    def verify_signature(self, image_ref: str, identity: str | None = None, issuer: str | None = None) -> VerificationResult:
        cmd = [self.bin_path, "verify", "--output", "json"]
        if identity and issuer:
            cmd.extend(["--certificate-identity", identity, "--certificate-oidc-issuer", issuer])
        elif identity:
            cmd.extend(["--certificate-identity", identity])
        elif issuer:
            cmd.extend(["--certificate-oidc-issuer", issuer])

        cmd.append(image_ref)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
        except subprocess.TimeoutExpired:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, error_message="Timeout")
        except FileNotFoundError:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, error_message="Cosign binary not found")

        if result.returncode != 0:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, error_message=result.stderr)

        try:
            # cosign returns a list of results
            data = json.loads(result.stdout)
            if not data or not isinstance(data, list):
                return VerificationResult(artifact_reference=image_ref, signature_valid=False, error_message="Invalid output format")

            first_sig = data[0]
            cert = first_sig.get("optional", {}).get("Subject", "")
            iss = first_sig.get("optional", {}).get("Issuer", "")

            return VerificationResult(
                artifact_reference=image_ref,
                signature_valid=True,
                signer_identity=cert,
                certificate_issuer=iss
            )

        except json.JSONDecodeError:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, error_message="JSON decode error")

    def verify_attestation(self, image_ref: str, identity: str | None = None, issuer: str | None = None) -> VerificationResult:
        cmd = [self.bin_path, "verify-attestation", "--type", "slsaprovenance", "--output", "json"]
        if identity and issuer:
            cmd.extend(["--certificate-identity", identity, "--certificate-oidc-issuer", issuer])

        cmd.append(image_ref)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
        except subprocess.TimeoutExpired:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, provenance_valid=False, error_message="Timeout")
        except FileNotFoundError:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, provenance_valid=False, error_message="Cosign binary not found")

        if result.returncode != 0:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, provenance_valid=False, error_message=result.stderr)

        try:
            data = json.loads(result.stdout)
            if not data:
                return VerificationResult(artifact_reference=image_ref, signature_valid=False, provenance_valid=False, error_message="Empty output")

            first_att = data[0]
            payload = first_att.get("payload")
            builder = None
            if payload:
                decoded = base64.b64decode(payload).decode('utf-8')
                prov = json.loads(decoded)
                builder = prov.get("predicate", {}).get("builder", {}).get("id")

            return VerificationResult(
                artifact_reference=image_ref,
                signature_valid=True,
                provenance_valid=True,
                builder=builder
            )

        except Exception as e:
            return VerificationResult(artifact_reference=image_ref, signature_valid=False, provenance_valid=False, error_message=str(e))
