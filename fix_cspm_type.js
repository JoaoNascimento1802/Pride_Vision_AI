const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/cspm.py', 'utf-8');

code = code.replace(/def ingest_cspm_event\([\s\S]*?\):/, `def ingest_cspm_event(
    event: CSPMEvent,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> dict[str, Any]:`);

if (!code.includes('from typing import Any')) {
    code = "from typing import Any\n" + code;
}

fs.writeFileSync('backend/app/routers/cspm.py', code, 'utf-8');
