const fs = require('fs');
let code = fs.readFileSync('backend/tests/test_runtime.py', 'utf-8');

code = code.replace(/uuid.uuid4\(, responsavel="Admin"\).hex\}/g, 'uuid.uuid4().hex}", responsavel="Admin"');
code = code.replace(/, responsavel="Admin"\)/g, ')'); // clean up trailing messed up things
code = code.replace('exposicao=Exposicao.INTERNA)', 'exposicao=Exposicao.INTERNA, responsavel="Admin")');

fs.writeFileSync('backend/tests/test_runtime.py', code, 'utf-8');
