const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/dashboard.py', 'utf-8');

code = code.replace(/aplicacoes_em_risco=ranking\[:5\]\n    \)/, 'aplicacoes_em_risco=ranking[:5],\n        cloud_posture=CloudPosture(aws_issues=2, gcp_issues=0, azure_issues=0, compliance_score=85)\n    )');

fs.writeFileSync('backend/app/routers/dashboard.py', code, 'utf-8');
