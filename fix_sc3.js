const fs = require('fs');

let sc = fs.readFileSync('backend/app/routers/supply_chain.py', 'utf-8');
sc = sc.replace('ArtifactVerification.criado_em', 'ArtifactVerification.verified_at');
sc = sc.replace('r.created_at', 'r.verified_at');

sc = sc.replace('def check_policy(policy, signature_valid: bool, provenance_valid: bool, identity: str = None, issuer: str = None):', 'def check_policy(policy: Policy, signature_valid: bool, provenance_valid: bool, identity: str | None = None, issuer: str | None = None) -> bool:');
sc = sc.replace('def check_policy(policy: Policy, signature_valid: bool, provenance_valid: bool, identity: str = None, issuer: str = None):', 'def check_policy(policy: Policy, signature_valid: bool, provenance_valid: bool, identity: str | None = None, issuer: str | None = None) -> bool:');

sc = sc.replace('def listar_verificacoes(image_name: str, db: Session = Depends(get_db)):', 'def listar_verificacoes(image_name: str, db: Session = Depends(get_db)) -> list[dict[str, str|bool|int|None]]:');

fs.writeFileSync('backend/app/routers/supply_chain.py', sc, 'utf-8');
