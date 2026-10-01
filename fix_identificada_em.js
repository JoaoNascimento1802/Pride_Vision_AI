const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/runtime.py', 'utf-8');

code = code.replace(/vuln.criado_em/g, 'vuln.identificada_em');
code = code.replace(/new_vuln.criado_em/g, 'new_vuln.identificada_em');

fs.writeFileSync('backend/app/routers/runtime.py', code, 'utf-8');
