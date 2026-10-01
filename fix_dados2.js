const fs = require('fs');
let code = fs.readFileSync('frontend/src/testes/dados.ts', 'utf-8');

code = code.replace(/aplicacoes_em_risco: \[\],\n\}/g, "aplicacoes_em_risco: [],\n  cloud_posture: { aws_issues: 0, gcp_issues: 0, azure_issues: 0, compliance_score: 100 }\n}");

fs.writeFileSync('frontend/src/testes/dados.ts', code, 'utf-8');
