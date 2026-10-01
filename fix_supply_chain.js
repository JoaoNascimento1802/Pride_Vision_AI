const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/supply_chain.py', 'utf-8');

code = code.replace(/def verificar_assinatura\((.*?)\):/s, 'def verificar_assinatura($1) -> dict:');
code = code.replace(/identity: str = None/g, 'identity: str | None = None');
code = code.replace(/issuer: str = None/g, 'issuer: str | None = None');

code = code.replace(/def consultar_provenance\((.*?)\):/s, 'def consultar_provenance($1) -> dict:');

fs.writeFileSync('backend/app/routers/supply_chain.py', code, 'utf-8');
