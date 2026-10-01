const fs = require('fs');
let code = fs.readFileSync('backend/app/main.py', 'utf-8');
code = code.replace('from app.routers import runtime,\n', 'from app.routers import runtime\n');
fs.writeFileSync('backend/app/main.py', code, 'utf-8');
