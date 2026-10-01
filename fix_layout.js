const fs = require('fs')

let code = fs.readFileSync('frontend/src/components/Layout.tsx', 'utf-8')
code = code.replace("{ para: '/auditoria', rotulo: 'Auditoria', exato: false, permissao: 'audit:read' },", "{ para: '/auditoria', rotulo: 'Auditoria', exato: false, permissao: 'audit:read' },\n  { para: '/observabilidade', rotulo: 'System Health', exato: false, permissao: 'audit:read' },")

fs.writeFileSync('frontend/src/components/Layout.tsx', code)
