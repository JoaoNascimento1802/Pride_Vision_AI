const fs = require('fs');
let code = fs.readFileSync('frontend/src/api/types.ts', 'utf-8');

const cloud_types = `
export interface CloudPosture {
  aws_issues: number;
  gcp_issues: number;
  azure_issues: number;
  compliance_score: number;
}
`;

code = cloud_types + code;

fs.writeFileSync('frontend/src/api/types.ts', code, 'utf-8');
