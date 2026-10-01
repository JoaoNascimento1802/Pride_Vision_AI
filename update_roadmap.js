const fs = require('fs');
let code = fs.readFileSync('ROADMAP_IMPLEMENTACAO.md', 'utf-8');

code = code.replace(/⚪ Cloud CSPM/, '✅ Cloud CSPM');
code = code.replace(/O próximo gap a ser implementado é:/, '✅ Cloud CSPM implementado.\n\nO próximo gap a ser implementado é:');

fs.writeFileSync('ROADMAP_IMPLEMENTACAO.md', code, 'utf-8');
