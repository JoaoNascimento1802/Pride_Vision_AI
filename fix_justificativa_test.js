const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_runtime.py', 'utf-8');

code = code.replace(/risco=Risco.ALTO,/g, 'risco=Risco.ALTO,\n        justificativa="Log4j detectado estaticamente",');

fs.writeFileSync('backend/tests/test_runtime.py', code, 'utf-8');
