const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_runtime.py', 'utf-8');

code = code.replace(/App Test/g, 'App Test RT1 ' + Math.random().toString().substring(2, 6));
code = code.replace(/App Test 2/g, 'App Test RT2 ' + Math.random().toString().substring(2, 6));

fs.writeFileSync('backend/tests/test_runtime.py', code, 'utf-8');
