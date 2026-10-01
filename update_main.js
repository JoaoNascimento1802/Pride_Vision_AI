const fs = require('fs');
let code = fs.readFileSync('backend/app/main.py', 'utf-8');

code = code.replace('from app.routers import (', 'from app.routers import runtime,\nfrom app.routers import (');
code = code.replace('app.include_router(supply_chain.router)', 'app.include_router(supply_chain.router)\napp.include_router(runtime.router)');

fs.writeFileSync('backend/app/main.py', code, 'utf-8');
