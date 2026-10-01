const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/runtime.py', 'utf-8');

code = code.replace(',\n                criado_em=datetime.now(UTC)', '');

fs.writeFileSync('backend/app/routers/runtime.py', code, 'utf-8');
