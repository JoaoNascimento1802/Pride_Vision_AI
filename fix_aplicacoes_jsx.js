const fs = require('fs');
let code = fs.readFileSync('frontend/src/pages/Aplicacoes.tsx', 'utf-8');

const cloud_tab = `
      <div className="mt-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Cloud Infrastructure (CSPM)</h3>
        <div className="bg-gray-50 border rounded p-4 text-sm text-gray-700">
          <p className="mb-2"><strong>Account:</strong> 123456789012 (AWS)</p>
          <p><strong>Recursos Ativos:</strong></p>
          <ul className="list-disc ml-6 mt-1">
            <li>arn:aws:s3:::meu-bucket-producao</li>
            <li>arn:aws:ec2:us-east-1:123456789012:instance/i-0abcd1234efgh5678 <span className="text-red-600 font-bold ml-2">⚠️ TOXIC COMBINATION DETECTED</span></li>
          </ul>
        </div>
      </div>
`

if (!code.includes("Cloud Infrastructure (CSPM)")) {
    code = code.replace(/<RelatoriosEmVigor\s+uploads=\{aplicacao\.uploads\}\s+carregando=\{false\}\s+\/>/, '<RelatoriosEmVigor\n          uploads={aplicacao.uploads}\n          carregando={false}\n        />\n' + cloud_tab);
    fs.writeFileSync('frontend/src/pages/Aplicacoes.tsx', code, 'utf-8');
}
