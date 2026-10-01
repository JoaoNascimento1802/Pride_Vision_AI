const fs = require('fs');

let m = fs.readFileSync('backend/app/main.py', 'utf-8');
m = m.replace('from app.routers import supply_chain\n', '');
m = m.replace('from app.routers import vulnerabilities, dashboard, applications, auth, integrations, ci', 'from app.routers import vulnerabilities, dashboard, applications, auth, integrations, ci, supply_chain');
fs.writeFileSync('backend/app/main.py', m, 'utf-8');

let i = fs.readFileSync('backend/app/models/__init__.py', 'utf-8');
i = i.replace('"SbomComponent",', '"SbomComponent", "ArtifactVerification",');
fs.writeFileSync('backend/app/models/__init__.py', i, 'utf-8');

let sc = fs.readFileSync('backend/app/routers/supply_chain.py', 'utf-8');
sc = sc.replace('Policy.ativa == True', 'Policy.ativa.is_(True)');
sc = sc.replace('Policy.aplicacao_id == None', 'Policy.aplicacao_id.is_(None)');
fs.writeFileSync('backend/app/routers/supply_chain.py', sc, 'utf-8');

let ts = fs.readFileSync('backend/tests/test_supply_chain.py', 'utf-8');
ts = ts.replace('kwargs.get("shell") != True', 'not kwargs.get("shell")');
fs.writeFileSync('backend/tests/test_supply_chain.py', ts, 'utf-8');
