const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_runtime.py', 'utf-8');

code = code.replace(/Ambiente.STAGING/g, 'Ambiente.HOMOLOGACAO');

fs.writeFileSync('backend/tests/test_runtime.py', code, 'utf-8');
