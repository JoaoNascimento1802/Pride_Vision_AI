const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/supply_chain.py', 'utf-8');

code = code.replace(/def verify_artifact\((.*?)\):/s, 'def verify_artifact($1) -> dict:');
code = code.replace(/def list_verifications\((.*?)\):/s, 'def list_verifications($1) -> list:');

fs.writeFileSync('backend/app/routers/supply_chain.py', code, 'utf-8');
