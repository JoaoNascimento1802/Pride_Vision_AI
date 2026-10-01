const fs = require('fs');
let code = fs.readFileSync('backend/app/services/normalizer.py', 'utf-8');

code = code.replace(/ferramenta=Ferramenta\.API_SECURITY,/g, 'origem=Ferramenta.API_SECURITY,');

fs.writeFileSync('backend/app/services/normalizer.py', code, 'utf-8');
