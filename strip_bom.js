const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/cspm.py', 'utf-8');

if (code.charCodeAt(0) === 0xFEFF) {
    code = code.slice(1);
}

code = code.replace(/if s == "CRITICAL": return Risco\.CRITICO/g, 'if s == "CRITICAL":\n        return Risco.CRITICO');
code = code.replace(/if s == "HIGH": return Risco\.ALTO/g, 'if s == "HIGH":\n        return Risco.ALTO');
code = code.replace(/if s == "MEDIUM": return Risco\.MEDIO/g, 'if s == "MEDIUM":\n        return Risco.MEDIO');

fs.writeFileSync('backend/app/routers/cspm.py', code, 'utf-8');
