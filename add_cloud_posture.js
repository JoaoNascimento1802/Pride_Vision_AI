const fs = require('fs');
let code = fs.readFileSync('backend/app/models/enums.py', 'utf-8');

if (!code.includes('CLOUD_POSTURE = "cloud_posture"')) {
    code = code.replace(/RUNTIME = "runtime"/, 'RUNTIME = "runtime"\n    CLOUD_POSTURE = "cloud_posture"');
    fs.writeFileSync('backend/app/models/enums.py', code, 'utf-8');
}
