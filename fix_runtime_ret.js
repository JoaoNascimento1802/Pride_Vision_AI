const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/runtime.py', 'utf-8');

code = code.replace(
    'db: Session = Depends(get_db)\n):',
    'db: Session = Depends(get_db)\n) -> RuntimeIngestionResponse:'
);

fs.writeFileSync('backend/app/routers/runtime.py', code, 'utf-8');
