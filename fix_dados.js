const fs = require('fs');
let code = fs.readFileSync('frontend/src/testes/dados.ts', 'utf-8');

const cloud_posture = `cloud_posture: { aws_issues: 2, gcp_issues: 0, azure_issues: 0, compliance_score: 85 }`;

code = code.replace(/aplicacoes_em_risco: \[\n    \{\n      id: 1,/, cloud_posture + ',\n  aplicacoes_em_risco: [\n    {\n      id: 1,');
code = code.replace(/aplicacoes_em_risco: \[\]\n\}/g, 'aplicacoes_em_risco: [],\n  ' + cloud_posture + '\n}');

fs.writeFileSync('frontend/src/testes/dados.ts', code, 'utf-8');
