const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/runtime.py', 'utf-8');

code = code.replace(/risco=vuln_risco,/g, 'risco=vuln_risco,\n                justificativa="Ameaça em execução (Runtime) reportada pelo agente.",');

fs.writeFileSync('backend/app/routers/runtime.py', code, 'utf-8');
