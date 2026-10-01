const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/cspm.py', 'utf-8');

code = code.replace(/app_id = resource.aplicacao_id\n    if not app_id:\n        app_id = 1 # Fallback/g, 'app_id = resource.aplicacao_id\n    if not app_id:\n        app_db = db.query(Application).first()\n        app_id = app_db.id if app_db else 1');

fs.writeFileSync('backend/app/routers/cspm.py', code, 'utf-8');
