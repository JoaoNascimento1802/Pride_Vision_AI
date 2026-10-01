const fs = require('fs');
let text = fs.readFileSync('frontend/src/pages/DetalheVulnerabilidade.tsx', 'utf-8');
const target = '<p className="border-t border-slate-100 pt-2 text-slate-600">{achado.mensagem}</p>';
const injection = '{achado.image_name && <ContainerVerifications imageName={achado.image_name} />}\n        ';
text = text.replace(target, injection + target);
fs.writeFileSync('frontend/src/pages/DetalheVulnerabilidade.tsx', text, 'utf-8');
