const fs = require('fs');
let code = fs.readFileSync('backend/app/main.py', 'utf-8');
code = code.replace(
`from app.routers import (
    applications,
    audit,
    auth,
    ci,
    dashboard,
    integrations,
    sboms,
    tickets,
    uploads,
    vulnerabilities,
)`, 
`from app.routers import (
    applications,
    audit,
    auth,
    ci,
    dashboard,
    integrations,
    sboms,
    supply_chain,
    tickets,
    uploads,
    vulnerabilities,
)`);
fs.writeFileSync('backend/app/main.py', code, 'utf-8');
