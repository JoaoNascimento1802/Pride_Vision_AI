const fs = require('fs');
let code = fs.readFileSync('frontend/src/pages/Dashboard.tsx', 'utf-8');

const cloud_posture_jsx = `
      <div className="bg-white border rounded-lg p-6 flex flex-col items-center justify-center">
        <h2 className="text-lg font-semibold mb-4 text-gray-700">Cloud Posture Overview</h2>
        <div className="flex gap-4">
          <Indicador rotulo="AWS Issues" valor={dados.cloud_posture?.aws_issues || 0} />
          <Indicador rotulo="GCP Issues" valor={dados.cloud_posture?.gcp_issues || 0} />
          <Indicador rotulo="Azure Issues" valor={dados.cloud_posture?.azure_issues || 0} />
        </div>
        <div className="mt-4 text-center">
          <span className="text-gray-500 text-sm">Compliance Score</span>
          <div className="text-3xl font-bold text-blue-600">{dados.cloud_posture?.compliance_score || 0}%</div>
        </div>
      </div>
`

if (!code.includes("Cloud Posture Overview")) {
    code = code.replace(
        /<div className="bg-white border rounded-lg p-6">[\s\S]*?<h2 className="text-lg font-semibold mb-4">Aplicações com mais risco<\/h2>/,
        cloud_posture_jsx + '\n      <div className="bg-white border rounded-lg p-6">\n        <h2 className="text-lg font-semibold mb-4">Aplicações com mais risco</h2>'
    );
    fs.writeFileSync('frontend/src/pages/Dashboard.tsx', code, 'utf-8');
}
