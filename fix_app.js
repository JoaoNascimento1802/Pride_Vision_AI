const fs = require('fs')

let code = fs.readFileSync('frontend/src/App.tsx', 'utf-8')
code = code.replace("import { Auditoria } from './pages/Auditoria'", "import { Auditoria } from './pages/Auditoria'\nimport { Observability } from './pages/Observability'")
code = code.replace('<Route path="/auditoria" element={<Auditoria />} />', '<Route path="/auditoria" element={<Auditoria />} />\n        <Route path="/observabilidade" element={<Observability />} />')

fs.writeFileSync('frontend/src/App.tsx', code)
