const fs = require('fs');
let code = fs.readFileSync('frontend/src/pages/__tests__/Dashboard.test.tsx', 'utf-8');

if (!code.includes("cloud_posture:")) {
    code = code.replace(/aplicacoes_em_risco: \[\],/, 'aplicacoes_em_risco: [],\n  cloud_posture: { aws_issues: 2, gcp_issues: 0, azure_issues: 0, compliance_score: 85 },');
    fs.writeFileSync('frontend/src/pages/__tests__/Dashboard.test.tsx', code, 'utf-8');
}
