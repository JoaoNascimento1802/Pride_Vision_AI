const fs = require('fs');
let code = fs.readFileSync('backend/app/routers/runtime.py', 'utf-8');

code = code.replace(/StatusVulnerabilidade.OPEN/g, 'StatusVulnerabilidade.NOVA');
code = code.replace(/StatusVulnerabilidade.IN_PROGRESS/g, 'StatusVulnerabilidade.EM_CORRECAO');

code = code.replace('SlaService.calculate_sla(db, vuln)', 'vuln.due_at = SlaService.calcular_due_date(vuln.risco, vuln.criado_em)');
code = code.replace('SlaService.calculate_sla(db, new_vuln)', 'new_vuln.due_at = SlaService.calcular_due_date(new_vuln.risco, new_vuln.criado_em)');

fs.writeFileSync('backend/app/routers/runtime.py', code, 'utf-8');
