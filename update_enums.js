const fs = require('fs');
let code = fs.readFileSync('backend/app/models/enums.py', 'utf-8');

code = code.replace('SUPPLY_CHAIN = "supply_chain"', 'SUPPLY_CHAIN = "supply_chain"\n    RUNTIME = "runtime"');
code = code.replace('"supply_chain": "Supply Chain",', '"supply_chain": "Supply Chain",\n            "runtime": "Runtime Security",');
fs.writeFileSync('backend/app/models/enums.py', code, 'utf-8');
