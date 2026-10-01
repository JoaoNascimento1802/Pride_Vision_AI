const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/supply_chain.py', 'utf-8');

code = code.replace(/-> dict:/g, '-> dict[str, Any]:');
code = code.replace(/-> list:/g, '-> list[dict[str, Any]]:');

// Make sure Any is imported
if (!code.includes('from typing import Any')) {
    code = 'from typing import Any\n' + code;
}

fs.writeFileSync('backend/app/routers/supply_chain.py', code, 'utf-8');
