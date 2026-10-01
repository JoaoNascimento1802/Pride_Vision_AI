const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_runtime.py', 'utf-8');

code = code.replace(',\n        criado_em=datetime.now(UTC)', '');

fs.writeFileSync('backend/tests/test_runtime.py', code, 'utf-8');
