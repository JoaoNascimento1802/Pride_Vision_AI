const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_cspm.py', 'utf-8');

code = code.replace(/importancia="critica"/g, 'importancia="alta"');

fs.writeFileSync('backend/tests/test_cspm.py', code, 'utf-8');
